from pydantic import BaseModel, Field
from typing import Optional

class Meeting(BaseModel):
    id: int
    meet_link: str
    youtube_link: Optional[str] = None
    status: str = Field(default="stopped")

    def start(self):
        self.status = "running"

    def stop(self):
        self.status = "stopped"
