#This file is responisbke to handle all the mongodb connection

#This file is responsible to handle all the mongodb connections
"""
MongoDB connection handling of Task Service.
Each Microservice own its own db - this a core microservice principle (no shared db between the services).
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME","task_service_db")

client = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]
task_collection = database.get_collection("tasks")


#MONGO DB -> DB(task_service_db) -> multiple collections(tables) -> tasks

#whenever u insert a data into mongo db, by default mongo db will have a placeholder or a unique
#key called as _id(object id)