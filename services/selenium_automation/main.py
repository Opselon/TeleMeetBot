import sys
import os
import threading
import traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium_automation import SeleniumAutomation
from meeting import Meeting
from services.common.logging import configure_logging
import structlog

# --- Logging Setup ---
configure_logging(service_name="selenium_automation")
logger = structlog.get_logger()

# --- Health/Startup Logging ---
logger.info("Service starting", service="selenium_automation")

# --- Global Exception Handler ---
import asyncio
def handle_exception(loop, context):
    logger.error("Unhandled exception", error=context.get("exception"), message=context.get("message"))
asyncio.get_event_loop().set_exception_handler(handle_exception)

app = FastAPI()
meetings: dict[int, Meeting] = {}
next_meeting_id = 0

class AutomationRequest(BaseModel):
    meet_link: str
    youtube_link: str = None

@app.post("/start")
def start_automation(request: AutomationRequest):
    global next_meeting_id
    meeting_id = next_meeting_id
    next_meeting_id += 1
    logger.info("/start endpoint called", meet_link=request.meet_link, youtube_link=request.youtube_link, meeting_id=meeting_id)
    meeting = Meeting(id=meeting_id, meet_link=request.meet_link, youtube_link=request.youtube_link)
    meetings[meeting_id] = meeting
    def automation_target(meeting: Meeting):
        try:
            selenium_automation = SeleniumAutomation(logger.bind(service="selenium_automation", meeting_id=meeting.id))
            meeting.start()
            if selenium_automation.start_driver():
                if selenium_automation.join_meet(meeting.meet_link):
                    if meeting.youtube_link:
                        selenium_automation.play_youtube_video(meeting.youtube_link)
                        selenium_automation.share_screen()
            logger.info("Automation thread completed", meeting_id=meeting.id)
        except Exception as e:
            logger.error("Error in automation thread", error=str(e), traceback=traceback.format_exc())
    automation_thread = threading.Thread(target=automation_target, args=(meeting,))
    automation_thread.start()
    return {"message": "Automation started successfully", "meeting_id": meeting_id}

class StopRequest(BaseModel):
    meeting_id: int

@app.post("/stop")
def stop_automation(request: StopRequest):
    logger.info("/stop endpoint called", meeting_id=request.meeting_id)
    meeting = meetings.get(request.meeting_id)
    if not meeting:
        logger.error("Meeting not found", meeting_id=request.meeting_id)
        raise HTTPException(status_code=404, detail="Meeting not found")
    meeting.stop()
    logger.info("Meeting stopped", meeting_id=request.meeting_id)
    return {"message": "Automation stopped successfully"}

@app.post("/mute")
def mute_microphone():
    logger.info("/mute endpoint called")
    if not selenium_automation:
        logger.error("Automation is not running for mute")
        raise HTTPException(status_code=400, detail="Automation is not running")
    selenium_automation.mute_microphone()
    logger.info("Microphone muted")
    return {"message": "Microphone muted successfully"}

@app.post("/unmute")
def unmute_microphone():
    logger.info("/unmute endpoint called")
    if not selenium_automation:
        logger.error("Automation is not running for unmute")
        raise HTTPException(status_code=400, detail="Automation is not running")
    selenium_automation.unmute_microphone()
    logger.info("Microphone unmuted")
    return {"message": "Microphone unmuted successfully"}

@app.get("/status")
def get_status():
    logger.info("/status endpoint called")
    return {
        "meetings": [meeting.dict() for meeting in meetings.values()]
    }

@app.get("/health")
def health():
    logger.info("/health endpoint called")
    return {"status": "healthy"}
