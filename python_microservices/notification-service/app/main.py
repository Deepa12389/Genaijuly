"""
Notification Service
=====================
Owns everything related to Notifications. Receives events from Task
Service (or any other service) via a plain REST endpoint and stores
them in its OWN MongoDB database (notification_service_db).

It has zero knowledge of how Task Service's database is structured -
it only knows the shape of the JSON payload sent to it. That's the
whole point of a microservice boundary.
"""
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from bson.errors import InvalidId

from app.database import notification_collection
from app.models import NotificationCreate, NotificationResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-service")

app = FastAPI(
    title="Notification Service",
    description="Microservice responsible for generating and storing notifications",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

EVENT_MESSAGES = {
    "task_created": "New task created: '{title}'",
    "task_completed": "Task completed: '{title}'",
}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "notification-service"}


@app.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(payload: NotificationCreate):
    message_template = EVENT_MESSAGES.get(payload.event, "Event '{event}' for task '{title}'")
    message = message_template.format(title=payload.title, event=payload.event)

    doc = {
        "task_id": payload.task_id,
        "title": payload.title,
        "event": payload.event,
        "message": message,
        "created_at": datetime.now(timezone.utc),
    }
    result = await notification_collection.insert_one(doc)
    doc["_id"] = result.inserted_id

    logger.info(f"Notification stored: {message}")
    return _doc_to_response(doc)


@app.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(limit: int = 50):
    notifications = []
    async for doc in notification_collection.find().sort("created_at", -1).limit(limit):
        notifications.append(_doc_to_response(doc))
    return notifications


@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: str):
    try:
        oid = ObjectId(notification_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid notification id format")

    doc = await notification_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Notification not found")
    return _doc_to_response(doc)


def _doc_to_response(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "task_id": doc["task_id"],
        "title": doc["title"],
        "event": doc["event"],
        "message": doc["message"],
        "created_at": doc["created_at"],
    }