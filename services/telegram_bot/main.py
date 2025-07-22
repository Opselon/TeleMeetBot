from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import os

app = FastAPI()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SELENIUM_AUTOMATION_API_URL = "http://selenium_automation:5003"

async def meet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a Google Meet link.")
        return
    meet_link = context.args[0]

    response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/start", json={"meet_link": meet_link})
    if response.status_code == 200:
        await update.message.reply_text("Automation started successfully.")
    else:
        await update.message.reply_text(f"Failed to start automation: {response.text}")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a YouTube link.")
        return
    youtube_link = context.args[0]

    # This assumes an automation is already running.
    # A more robust implementation would store the current automation state.
    response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/play_youtube", json={"youtube_link": youtube_link})
    if response.status_code == 200:
        await update.message.reply_text("Playing YouTube video.")
    else:
        await update.message.reply_text(f"Failed to play video: {response.text}")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/stop")
    if response.status_code == 200:
        await update.message.reply_text("Automation stopped successfully.")
    else:
        await update.message.reply_text(f"Failed to stop automation: {response.text}")

from common.logging import configure_logging
import structlog

configure_logging()
logger = structlog.get_logger()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Telegram bot")
    if TELEGRAM_TOKEN:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("meet", meet))
        application.add_handler(CommandHandler("play", play))
        application.add_handler(CommandHandler("stop", stop))
        application.run_polling()
    else:
        logger.warning("TELEGRAM_TOKEN not set, bot will not start")

@app.get("/status")
def get_status():
    return {"status": "running"}
