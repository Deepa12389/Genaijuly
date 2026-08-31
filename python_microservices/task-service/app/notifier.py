#HTTP client that calls the notification, whenever a task has been created, modified this file is responsible to trigger the notification service#HTTP client that calls notification
"""
to call the notfication service from the task service, whenever task microservice is been triggered and worked upon , post the completeion of it the notification
service will be triggered , and this file is responsible to trigger the notification service post the task has been created or modified
"""
import os
import httpx
import logging

logger = logging.getLogger("task-service.notifier")

NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8001")

async def notify(task_id: str, title: str, event: str) -> None:
    """
    Fire-and-forget style notification call.
    event examples: "task_created", "task_completed"
    """
    payload = {
        "task_id": task_id,
        "title": title,
        "event": event,
    }
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(
                f"{NOTIFICATION_SERVICE_URL}/notifications", json=payload
            )
            response.raise_for_status()
            logger.info(f"Notification sent for task {task_id} ({event})")
    except Exception as exc:
        # Deliberately swallow the error - Task Service's job (managing
        # tasks) must not fail just because Notification Service is
        # unavailable. In a production system you'd push this to a retry
        # queue (e.g. Celery/RabbitMQ) instead of just logging.
        logger.warning(f"Could not notify for task {task_id}: {exc}")