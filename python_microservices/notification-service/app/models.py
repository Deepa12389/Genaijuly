from pydantic import BaseModel
from datetime import datetime


# What Task Service (or anyone) sends us to create a notification
class NotificationCreate(BaseModel):
    task_id: str
    title: str
    event: str  # e.g. "task_created", "task_completed"


# What we return to clients
class NotificationResponse(BaseModel):
    id: str
    task_id: str
    title: str
    event: str
    message: str
    created_at: datetime