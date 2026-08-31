#Pydantic request

#Pydantic request
"""
Pydantic models for request/response vlaidation in Task Service
"""
from pydantic import BaseModel , Field
from typing import Optional
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskPriority(str,Enum):
    low="low"
    medium="medium"
    high="high"

# What the client sends when CREATING a task
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=1000)
    priority: TaskPriority = TaskPriority.medium


# What the client sends when UPDATING a task
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


# What the API returns to the client
class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime    