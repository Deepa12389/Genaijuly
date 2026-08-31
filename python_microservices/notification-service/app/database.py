"""
MongoDB connection for Notification Service.
Note: this is a COMPLETELY SEPARATE database from Task Service's database.
This is what makes it a true microservice rather than a shared-DB monolith.
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "notification_service_db")

client = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]
notification_collection = database.get_collection("notifications")