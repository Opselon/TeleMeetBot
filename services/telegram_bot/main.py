from fastapi import FastAPI
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import os
from dotenv import load_dotenv
import structlog

load_dotenv()

app = FastAPI()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SELENIUM_AUTOMATION_API_URL = "http://selenium_automation:5003"

from common.logging import configure_logging

configure_logging()
logger = structlog.get_logger(__name__)

async def meet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /meet command", chat_id=update.effective_chat.id, args=context.args)
    if not context.args:
        logger.warning("/meet command received without a link", chat_id=update.effective_chat.id)
        await update.message.reply_text("Please provide a Google Meet link.")
        return
    meet_link = context.args[0]

    try:
        response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/start", json={"meet_link": meet_link})
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        logger.info("Automation started successfully", meet_link=meet_link)
        await update.message.reply_text("Automation started successfully.")
    except requests.exceptions.RequestException as e:
        logger.error("Failed to start automation", meet_link=meet_link, exc_info=True)
        await update.message.reply_text(f"Failed to start automation: {e}")
    except Exception as e:
        logger.error("An unexpected error occurred in meet command", meet_link=meet_link, exc_info=True)
        await update.message.reply_text(f"An unexpected error occurred: {e}")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /play command", chat_id=update.effective_chat.id, args=context.args)
    if not context.args:
        logger.warning("/play command received without a link", chat_id=update.effective_chat.id)
        await update.message.reply_text("Please provide a YouTube link.")
        return
    youtube_link = context.args[0]

    try:
        # This assumes an automation is already running.
        # A more robust implementation would store the current automation state.
        response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/play_youtube", json={"youtube_link": youtube_link})
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        logger.info("Playing YouTube video", youtube_link=youtube_link)
        await update.message.reply_text("Playing YouTube video.")
    except requests.exceptions.RequestException as e:
        logger.error("Failed to play video", youtube_link=youtube_link, exc_info=True)
        await update.message.reply_text(f"Failed to play video: {e}")
    except Exception as e:
        logger.error("An unexpected error occurred in play command", youtube_link=youtube_link, exc_info=True)
        await update.message.reply_text(f"An unexpected error occurred: {e}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /stop command", chat_id=update.effective_chat.id)
    try:
        response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/stop")
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        logger.info("Automation stopped successfully")
        await update.message.reply_text("Automation stopped successfully.")
    except requests.exceptions.RequestException as e:
        logger.error("Failed to stop automation", exc_info=True)
        await update.message.reply_text(f"Failed to stop automation: {e}")
    except Exception as e:
        logger.error("An unexpected error occurred in stop command", exc_info=True)
        await update.message.reply_text(f"An unexpected error occurred: {e}")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Telegram bot")
    if TELEGRAM_TOKEN:
        try:
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            application.add_handler(CommandHandler("meet", meet))
            application.add_handler(CommandHandler("play", play))
            application.add_handler(CommandHandler("stop", stop))
            logger.info("Telegram bot handlers added, starting polling")
            application.run_polling()
        except Exception as e:
            logger.error("Error during Telegram bot startup", exc_info=True)
    else:
        logger.warning("TELEGRAM_TOKEN not set, bot will not start")

@app.get("/status")
def get_status():
    logger.info("Status check requested")
    return {"status": "running"}
