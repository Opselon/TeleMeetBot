import sys
import os
import traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from services.common.logging import configure_logging
import structlog
import asyncio

# --- Logging Setup ---
configure_logging(service_name="web_panel")
logger = structlog.get_logger()

# --- Health/Startup Logging ---
logger.info("Service starting", service="web_panel")

# --- Global Exception Handler ---
def handle_exception(loop, context):
    logger.error("Unhandled exception", error=context.get("exception"), message=context.get("message"))
asyncio.get_event_loop().set_exception_handler(handle_exception)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

TELEGRAM_BOT_API_URL = "http://telegram_bot:5002"
SELENIUM_AUTOMATION_API_URL = "http://selenium_automation:5003"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logger.info("/ root endpoint called")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run_automation")
async def run_automation(request: Request):
    data = await request.json()
    meet_link = data.get("meet_link")
    youtube_link = data.get("youtube_link")
    logger.info("/run_automation endpoint called", meet_link=meet_link, youtube_link=youtube_link)
    try:
        response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/start", json={"meet_link": meet_link, "youtube_link": youtube_link})
        logger.info("Automation start request sent", status_code=response.status_code)
        return response.json()
    except Exception as e:
        logger.error("Error in /run_automation", error=str(e), traceback=traceback.format_exc())
        return {"error": "Internal error occurred."}

@app.post("/stop_automation")
async def stop_automation():
    logger.info("/stop_automation endpoint called")
    try:
        response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/stop")
        logger.info("Automation stop request sent", status_code=response.status_code)
        return response.json()
    except Exception as e:
        logger.error("Error in /stop_automation", error=str(e), traceback=traceback.format_exc())
        return {"error": "Internal error occurred."}

@app.get("/status")
async def get_status():
    logger.info("/status endpoint called")
    try:
        telegram_response = requests.get(f"{TELEGRAM_BOT_API_URL}/status")
        telegram_status = telegram_response.json().get('status', 'offline')
    except requests.exceptions.RequestException:
        telegram_status = 'offline'
    try:
        selenium_response = requests.get(f"{SELENIUM_AUTOMATION_API_URL}/status")
        selenium_status = selenium_response.json().get('status', 'offline')
    except requests.exceptions.RequestException:
        selenium_status = 'offline'
    return {
        'telegram_bot': telegram_status,
        'selenium_automation': selenium_status
    }

@app.get("/health")
async def health():
    logger.info("/health endpoint called")
    return {"status": "healthy"}
