#Fast API
"""
owns everything related to tasks: create, read, update and also delete.
has its own mongo db
talks to notification service over http whenever a task is created
or completed - it never touches the notification services databse directly
"""

import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from bson.errors import InvalidId

from app.database import task_collection
from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus
from app.utils import task_doc_to_response
from app.notifier import notify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task-service")

app = FastAPI(
    title="Task Service",
    description="Microservice responsible for managing tasks",
    version="1.0.0",
)

# Allow the frontend (served from a different origin/port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in real production use
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Used by Docker/orchestrators to know if this service is alive."""
    return {"status": "ok", "service": "task-service"}


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    now = datetime.now(timezone.utc)
    doc = {
        "title": task.title,
        "description": task.description,
        "status": TaskStatus.pending.value,
        "priority": task.priority.value,
        "created_at": now,
        "updated_at": now,
    }
    result = await task_collection.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Inter-service call: tell Notification Service a task was created.
    # This does not block task creation from succeeding if it fails.
    await notify(task_id=str(result.inserted_id), title=task.title, event="task_created")

    return task_doc_to_response(doc)


@app.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(status_filter: TaskStatus | None = None):
    query = {}
    if status_filter:
        query["status"] = status_filter.value

    tasks = []
    async for doc in task_collection.find(query).sort("created_at", -1):
        tasks.append(task_doc_to_response(doc))
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    doc = await _find_task_or_404(task_id)
    return task_doc_to_response(doc)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, update: TaskUpdate):
    existing = await _find_task_or_404(task_id)

    update_data = {k: v for k, v in update.model_dump(exclude_unset=True).items() if v is not None}
    if "status" in update_data:
        update_data["status"] = update_data["status"].value if hasattr(update_data["status"], "value") else update_data["status"]
    if "priority" in update_data:
        update_data["priority"] = update_data["priority"].value if hasattr(update_data["priority"], "value") else update_data["priority"]

    update_data["updated_at"] = datetime.now(timezone.utc)

    await task_collection.update_one({"_id": ObjectId(task_id)}, {"$set": update_data})
    updated_doc = await task_collection.find_one({"_id": ObjectId(task_id)})

    # If the task just got marked completed, fire a notification
    if update_data.get("status") == TaskStatus.completed.value and existing["status"] != TaskStatus.completed.value:
        await notify(task_id=task_id, title=updated_doc["title"], event="task_completed")

    return task_doc_to_response(updated_doc)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    await _find_task_or_404(task_id)
    await task_collection.delete_one({"_id": ObjectId(task_id)})
    return None


async def _find_task_or_404(task_id: str) -> dict:
    try:
        oid = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid task id format")

    doc = await task_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Task not found")
    return doc