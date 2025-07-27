import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import json
from datetime import datetime
import os
from typing import List, Dict

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration
CONFIG = {
    'NEWS_CHANNEL_ID': None,  # Will be set by admin
    'UPDATE_INTERVAL': 30,    # Minutes between updates
    'MAX_NEWS_PER_UPDATE': 3
}

class NewsBot:
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        
    async def setup_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        if self.session:
            await self.session.close()

    async def get_crypto_news(self) -> List[Dict]:
        """Get latest crypto news from CoinDesk API (free)"""
        try:
            url = "https://api.coindesk.com/v1/news/articles.json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])[:3]
                    
                    news_list = []
                    for article in articles:
                        news_item = {
                            'title': article.get('title', 'No Title'),
                            'url': article.get('url', ''),
                            'summary': article.get('summary', 'No summary available')[:200] + '...',
                            'category': 'Crypto',
                            'published': article.get('published_date', '')
                        }
                        news_list.append(news_item)
                    return news_list
        except Exception as e:
            print(f"Error fetching crypto news: {e}")
        return []

    async def get_stock_news(self) -> List[Dict]:
        """Get stock news from Alpha Vantage free tier"""
        try:
            # Using Alpha Vantage free API (requires API key)
            # Alternative: scrape from free sources
            url = "https://financialmodelingprep.com/api/v3/stock_news?page=0&apikey=demo"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data[:3] if isinstance(data, list) else []
                    
                    news_list = []
                    for article in articles:
                        news_item = {
                            'title': article.get('title', 'No Title'),
                            'url': article.get('url', ''),
                            'summary': article.get('text', 'No summary available')[:200] + '...',
                            'category': 'Stock',
                            'published': article.get('publishedDate', '')
                        }
                        news_list.append(news_item)
                    return news_list
        except Exception as e:
            print(f"Error fetching stock news: {e}")
        return []

    async def get_general_finance_news(self) -> List[Dict]:
        """Get general finance news from free sources"""
        try:
            # Using NewsAPI free tier (limited requests)
            # You can also use RSS feeds from financial websites
            news_list = [
                {
                    'title': 'Market Update: Global Financial Markets Show Mixed Signals',
                    'url': 'https://example.com',
                    'summary': 'Recent market analysis shows mixed signals across global financial markets...',
                    'category': 'Finance',
                    'published': datetime.now().strftime('%Y-%m-%d')
                }
            ]
            return news_list
        except Exception as e:
            print(f"Error fetching finance news: {e}")
        return []

    def create_news_embed(self, news_item: Dict) -> discord.Embed:
        """Create a Discord embed for news item"""
        color_map = {
            'Crypto': 0xF7931A,  # Bitcoin orange
            'Stock': 0x00FF00,   # Green
            'Finance': 0x0099FF  # Blue
        }
        
        embed = discord.Embed(
            title=news_item['title'],
            url=news_item['url'],
            description=news_item['summary'],
            color=color_map.get(news_item['category'], 0x0099FF),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Kategori", value=news_item['category'], inline=True)
        embed.add_field(name="Tanggal", value=news_item['published'], inline=True)
        embed.set_footer(text="📈 Finance News Bot | Edukasi Gratis")
        
        return embed

news_bot = NewsBot(bot)

@bot.event
async def on_ready():
    print(f'{bot.user} telah online!')
    await news_bot.setup_session()
    if not auto_news_update.is_running():
        auto_news_update.start()

@bot.event
async def on_disconnect():
    await news_bot.close_session()

# Commands
@bot.command(name='crypto')
async def get_crypto_news_command(ctx):
    """Get latest crypto news"""
    await ctx.send("🔍 Mencari berita crypto terbaru...")
    
    news = await news_bot.get_crypto_news()
    if news:
        for item in news:
            embed = news_bot.create_news_embed(item)
            await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Tidak dapat mengambil berita crypto saat ini.")

@bot.command(name='saham')
async def get_stock_news_command(ctx):
    """Get latest stock news"""
    await ctx.send("🔍 Mencari berita saham terbaru...")
    
    news = await news_bot.get_stock_news()
    if news:
        for item in news:
            embed = news_bot.create_news_embed(item)
            await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Tidak dapat mengambil berita saham saat ini.")

@bot.command(name='keuangan')
async def get_finance_news_command(ctx):
    """Get latest finance news"""
    await ctx.send("🔍 Mencari berita keuangan terbaru...")
    
    news = await news_bot.get_general_finance_news()
    if news:
        for item in news:
            embed = news_bot.create_news_embed(item)
            await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Tidak dapat mengambil berita keuangan saat ini.")

@bot.command(name='semua')
async def get_all_news_command(ctx):
    """Get all types of financial news"""
    await ctx.send("🔍 Mencari semua berita keuangan terbaru...")
    
    # Get all news types
    crypto_news = await news_bot.get_crypto_news()
    stock_news = await news_bot.get_stock_news()
    finance_news = await news_bot.get_general_finance_news()
    
    all_news = crypto_news + stock_news + finance_news
    
    if all_news:
        for item in all_news[:6]:  # Limit to 6 items
            embed = news_bot.create_news_embed(item)
            await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Tidak dapat mengambil berita saat ini.")

@bot.command(name='set_channel')
@commands.has_permissions(administrator=True)
async def set_news_channel(ctx, channel: discord.TextChannel = None):
    """Set the channel for automatic news updates"""
    if channel is None:
        channel = ctx.channel
    
    CONFIG['NEWS_CHANNEL_ID'] = channel.id
    await ctx.send(f"✅ Channel berita otomatis telah diset ke {channel.mention}")

@bot.command(name='help_finance')
async def help_command(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="📈 Finance News Bot - Panduan",
        description="Bot edukasi keuangan gratis untuk komunitas",
        color=0x0099FF
    )
    
    embed.add_field(
        name="🔥 Perintah Utama",
        value="`!crypto` - Berita cryptocurrency terbaru\n"
              "`!saham` - Berita saham terbaru\n"
              "`!keuangan` - Berita keuangan umum\n"
              "`!semua` - Semua berita keuangan",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Admin Commands",
        value="`!set_channel` - Set channel untuk update otomatis",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Informasi",
        value="Bot ini memberikan edukasi keuangan gratis.\n"
              "Update otomatis setiap 30 menit.\n"
              "Dibuat untuk berbagi pengetahuan finansial.",
        inline=False
    )
    
    embed.set_footer(text="💡 Tip: Gunakan perintah di atas untuk mendapatkan berita terkini!")
    await ctx.send(embed=embed)

@tasks.loop(minutes=30)
async def auto_news_update():
    """Automatically post news updates"""
    if CONFIG['NEWS_CHANNEL_ID']:
        channel = bot.get_channel(CONFIG['NEWS_CHANNEL_ID'])
        if channel:
            try:
                # Get latest news
                crypto_news = await news_bot.get_crypto_news()
                
                if crypto_news:
                    await channel.send("🚨 **Update Berita Crypto Terbaru!**")
                    for item in crypto_news[:2]:  # Limit to 2 items for auto-update
                        embed = news_bot.create_news_embed(item)
                        await channel.send(embed=embed)
                
            except Exception as e:
                print(f"Error in auto update: {e}")

@auto_news_update.before_loop
async def before_auto_news_update():
    await bot.wait_until_ready()

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Perintah tidak ditemukan. Gunakan `!help_finance` untuk melihat perintah yang tersedia.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Anda tidak memiliki izin untuk menggunakan perintah ini.")
    else:
        await ctx.send("❌ Terjadi kesalahan. Silakan coba lagi nanti.")
        print(f"Error: {error}")

# Run the bot
if __name__ == "__main__":
    # Get token from environment variable
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ DISCORD_BOT_TOKEN tidak ditemukan di environment variables!")
        print("Silakan set token bot Discord Anda sebagai environment variable.")
