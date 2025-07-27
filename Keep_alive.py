from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return """
    <h1>🤖 Discord Finance News Bot</h1>
    <p>Bot is running and providing financial news!</p>
    <h2>Features:</h2>
    <ul>
        <li>📈 Crypto News</li>
        <li>📊 Stock News</li>
        <li>💰 Finance News</li>
        <li>🔄 Auto Updates</li>
    </ul>
    """

@app.route('/status')
def status():
    return {"status": "online", "message": "Bot is running"}

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
