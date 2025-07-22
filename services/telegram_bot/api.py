from flask import Flask, jsonify, request
import threading
from telegram_bot import TelegramBot
import os

app = Flask(__name__)

telegram_bot = None
bot_thread = None

@app.route('/start', methods=['POST'])
def start_bot():
    global telegram_bot, bot_thread
    token = Config.TELEGRAM_TOKEN
    if not token:
        return jsonify({"error": "Telegram token is not set"}), 400

    try:
        telegram_bot = TelegramBot(token, None, print)
        bot_thread = threading.Thread(target=telegram_bot.run, daemon=True)
        bot_thread.start()
        return jsonify({"message": "Telegram bot started successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to start Telegram bot: {e}"}), 500

@app.route('/stop', methods=['POST'])
def stop_bot():
    global telegram_bot
    if telegram_bot:
        # This is a simplified stop, a real implementation would need a more graceful shutdown
        telegram_bot = None
        return jsonify({"message": "Telegram bot stopped successfully"})
    else:
        return jsonify({"error": "Telegram bot is not running"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
