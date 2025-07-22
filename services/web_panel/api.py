from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base, Automation, Log, init_db
from selenium_automation import SeleniumAutomation
import threading
import uvicorn
from datetime import datetime
from telegram_bot import start_telegram_bot
from database import set_config, get_config

# Initialize the database
init_db()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
selenium_automation = None
automation_thread = None

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_message(db: Session, automation_id: int, message: str, level: str = "INFO"):
    log = Log(automation_id=automation_id, timestamp=datetime.utcnow(), level=level, message=message)
    db.add(log)
    db.commit()

@app.on_event("startup")
async def startup_event():
    start_telegram_bot()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    automations = db.query(Automation).all()
    token = get_config("telegram_token")
    return templates.TemplateResponse("index.html", {"request": request, "automations": automations, "telegram_token": token})

@app.post("/save_token")
async def save_token(request: Request):
    data = await request.form()
    token = data.get("token")
    set_config("telegram_token", token)
    return JSONResponse(content={"message": "Token saved successfully"})

@app.post("/run_automation")
async def run_automation(request: Request, db: Session = Depends(get_db)):
    global selenium_automation, automation_thread
    data = await request.json()
    meet_link = data.get("meet_link")
    youtube_link = data.get("youtube_link")

    if not meet_link:
        raise HTTPException(status_code=400, detail="Meet link is required")

    automation = Automation(meet_link=meet_link, youtube_link=youtube_link, status="Starting")
    db.add(automation)
    db.commit()
    db.refresh(automation)

    def automation_target(automation_id, meet_link, youtube_link):
        with SessionLocal() as db_session:
            def logger(message, level="INFO"):
                log_message(db_session, automation_id, message, level)

            global selenium_automation
            selenium_automation = SeleniumAutomation(logger)

            automation = db_session.query(Automation).filter(Automation.id == automation_id).first()
            automation.status = "Running"
            db_session.commit()

            if selenium_automation.start_driver():
                if selenium_automation.join_meet(meet_link):
                    if youtube_link:
                        selenium_automation.play_youtube_video(youtube_link)
                        selenium_automation.share_screen()

    automation_thread = threading.Thread(target=automation_target, args=(automation.id, meet_link, youtube_link))
    automation_thread.start()

    return JSONResponse(content={"message": "Automation started successfully", "automation_id": automation.id})

@app.post("/stop_automation")
async def stop_automation(request: Request, db: Session = Depends(get_db)):
    global selenium_automation, automation_thread
    data = await request.json()
    automation_id = data.get("automation_id")

    if not automation_id:
        raise HTTPException(status_code=400, detail="Automation ID is required")

    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    if selenium_automation:
        selenium_automation.stop_automation()
        if automation_thread and automation_thread.is_alive():
            automation_thread.join()
        selenium_automation = None
        automation_thread = None

    automation.status = "Stopped"
    db.commit()

    return JSONResponse(content={"message": "Automation stopped successfully"})

@app.get("/automations/{automation_id}/logs")
async def get_logs(automation_id: int, db: Session = Depends(get_db)):
    logs = db.query(Log).filter(Log.automation_id == automation_id).all()
    return logs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
