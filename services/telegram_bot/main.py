from contextlib import asynccontextmanager
from fastapi import FastAPI
import sys
import os
import asyncio
import traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import os
from dotenv import load_dotenv
from services.common.logging import configure_logging
import structlog

# --- Logging Setup ---
configure_logging(service_name="telegram_bot")
logger = structlog.get_logger()

# --- Load Environment ---
load_dotenv()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SELENIUM_AUTOMATION_API_URL = "http://selenium_automation:5003"

# --- Health/Startup Logging ---
logger.info("Service starting", service="telegram_bot")
if TELEGRAM_TOKEN:
    logger.info("TELEGRAM_TOKEN loaded", present=True)
else:
    logger.error("TELEGRAM_TOKEN not set", present=False)

# --- Global Exception Handler ---
def handle_exception(loop, context):
    logger.error("Unhandled exception", error=context.get("exception"), message=context.get("message"))

asyncio.get_event_loop().set_exception_handler(handle_exception)

# --- Telegram Bot Logic ---
async def run_telegram_bot():
    logger.info("Initializing Telegram bot")
    if TELEGRAM_TOKEN:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("meet", meet))
        application.add_handler(CommandHandler("play", play))
        application.add_handler(CommandHandler("stop", stop))
        logger.info("Handlers registered, starting polling")
        await application.run_polling()
    else:
        logger.error("TELEGRAM_TOKEN not set, bot will not start")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI lifespan starting, launching bot task")
    asyncio.create_task(run_telegram_bot())
    yield
    logger.info("FastAPI lifespan ended")

app = FastAPI(lifespan=lifespan)

async def meet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/meet command received", args=context.args)
    if not context.args:
        await update.message.reply_text("Please provide a Google Meet link.")
        return
    meet_link = context.args[0]
    try:
        response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/start", json={"meet_link": meet_link})
        if response.status_code == 200:
            await update.message.reply_text("Automation started successfully.")
        else:
            await update.message.reply_text(f"Failed to start automation: {response.text}")
        logger.info("/meet command processed", status_code=response.status_code)
    except Exception as e:
        logger.error("Error in /meet command", error=str(e), traceback=traceback.format_exc())
        await update.message.reply_text("Internal error occurred.")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/play command received", args=context.args)
    if not context.args:
        await update.message.reply_text("Please provide a YouTube link.")
        return
    youtube_link = context.args[0]
    try:
        response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/play_youtube", json={"youtube_link": youtube_link})
        if response.status_code == 200:
            await update.message.reply_text("Playing YouTube video.")
        else:
            await update.message.reply_text(f"Failed to play video: {response.text}")
        logger.info("/play command processed", status_code=response.status_code)
    except Exception as e:
        logger.error("Error in /play command", error=str(e), traceback=traceback.format_exc())
        await update.message.reply_text("Internal error occurred.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/stop command received")
    try:
        response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/stop")
        if response.status_code == 200:
            await update.message.reply_text("Automation stopped successfully.")
        else:
            await update.message.reply_text(f"Failed to stop automation: {response.text}")
        logger.info("/stop command processed", status_code=response.status_code)
    except Exception as e:
        logger.error("Error in /stop command", error=str(e), traceback=traceback.format_exc())
        await update.message.reply_text("Internal error occurred.")

@app.get("/status")
def get_status():
    logger.info("/status endpoint called")
    return {"status": "running"}

@app.get("/health")
def health():
    logger.info("/health endpoint called")
    return {"status": "healthy"}
