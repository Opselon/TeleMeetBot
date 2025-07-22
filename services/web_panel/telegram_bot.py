import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import SessionLocal
from selenium_automation import SeleniumAutomation
import threading
from api import log_message, app
from database import Automation
import requests

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(self.token).build()
        self.application.add_handler(CommandHandler("meet", self.meet))
        self.application.add_handler(CommandHandler("play", self.play))
        self.application.add_handler(CommandHandler("stop", self.stop))

    async def meet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Please provide a Google Meet link.")
            return
        meet_link = context.args[0]

        response = requests.post(f"http://127.0.0.1:5001/run_automation", json={"meet_link": meet_link})
        if response.status_code == 200:
            await update.message.reply_text("Automation started successfully.")
        else:
            await update.message.reply_text("Failed to start automation.")

    async def play(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("This feature is not yet implemented via Telegram.")

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("This feature is not yet implemented via Telegram.")

    def run(self):
        self.application.run_polling()

def start_telegram_bot():
    # In a real application, you would get the token from a secure source
    token = "YOUR_TELEGRAM_BOT_TOKEN"
    if token and token != "YOUR_TELEGRAM_BOT_TOKEN":
        bot = TelegramBot(token)
        thread = threading.Thread(target=bot.run)
        thread.start()
