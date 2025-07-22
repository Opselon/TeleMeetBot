import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from common.logging import configure_logging
import structlog
import uvicorn

configure_logging()
logger = structlog.get_logger()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

TELEGRAM_BOT_API_URL = "http://telegram_bot:5002"
SELENIUM_AUTOMATION_API_URL = "http://selenium_automation:5003"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run_automation")
async def run_automation(request: Request):
    data = await request.json()
    meet_link = data.get("meet_link")
    youtube_link = data.get("youtube_link")

    response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/start", json={"meet_link": meet_link, "youtube_link": youtube_link})
    return response.json()

@app.post("/stop_automation")
async def stop_automation():
    response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/stop")
    return response.json()

@app.get("/status")
async def get_status():
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

logger.info("Starting uvicorn server")
uvicorn.run(app, host="0.0.0.0", port=5001)
