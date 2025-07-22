from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium_automation import SeleniumAutomation
import threading

from meeting import Meeting

app = FastAPI()
meetings: dict[int, Meeting] = {}
next_meeting_id = 0

class AutomationRequest(BaseModel):
    meet_link: str
    youtube_link: str = None

from common.logging import configure_logging
import structlog

configure_logging()
logger = structlog.get_logger()

@app.post("/start")
def start_automation(request: AutomationRequest):
    global next_meeting_id
    meeting_id = next_meeting_id
    next_meeting_id += 1

    meeting = Meeting(id=meeting_id, meet_link=request.meet_link, youtube_link=request.youtube_link)
    meetings[meeting_id] = meeting

    def automation_target(meeting: Meeting):
        selenium_automation = SeleniumAutomation(logger.bind(service="selenium_automation", meeting_id=meeting.id))
        meeting.start()
        if selenium_automation.start_driver():
            if selenium_automation.join_meet(meeting.meet_link):
                if meeting.youtube_link:
                    selenium_automation.play_youtube_video(meeting.youtube_link)
                    selenium_automation.share_screen()

    automation_thread = threading.Thread(target=automation_target, args=(meeting,))
    automation_thread.start()

    return {"message": "Automation started successfully", "meeting_id": meeting_id}

class StopRequest(BaseModel):
    meeting_id: int

@app.post("/stop")
def stop_automation(request: StopRequest):
    meeting = meetings.get(request.meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # This is a simplified approach. In a real-world scenario, you would
    # need a more sophisticated way to stop the correct automation thread.
    meeting.stop()
    return {"message": "Automation stopped successfully"}

@app.post("/mute")
def mute_microphone():
    if not selenium_automation:
        raise HTTPException(status_code=400, detail="Automation is not running")
    selenium_automation.mute_microphone()
    return {"message": "Microphone muted successfully"}

@app.post("/unmute")
def unmute_microphone():
    if not selenium_automation:
        raise HTTPException(status_code=400, detail="Automation is not running")
    selenium_automation.unmute_microphone()
    return {"message": "Microphone unmuted successfully"}

@app.get("/status")
def get_status():
    return {
        "meetings": [meeting.dict() for meeting in meetings.values()]
    }
