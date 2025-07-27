import sys
import os
import asyncio
from bot import bot
from config import BOT_TOKEN

def check_requirements():
    """Check if all requirements are met"""
    if not BOT_TOKEN:
        print("❌ ERROR: DISCORD_BOT_TOKEN tidak ditemukan!")
        print("Silakan set environment variable DISCORD_BOT_TOKEN")
        return False
    
    print("✅ Bot token ditemukan")
    return True

def main():
    """Main startup function"""
    print("🚀 Memulai Discord Finance News Bot...")
    
    if not check_requirements():
        sys.exit(1)
    
    try:
        print("📡 Connecting to Discord...")
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
