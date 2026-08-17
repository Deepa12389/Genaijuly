from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI(
    title="Order",
    description="order API using FastAPI and Mongo",
    version="1.0"
)

#You have to establish the connection with the db
client = MongoClient("mongodb://localhost:27017/")
db = client["training_db"]
collection = db["orders"]

@app.post("/orders")
def create_orders(orders : dict):
    result = collection.insert_one(orders)

    return{
        "message":"orders data has been created",
        "_id" : str(result.inserted_id)
    }




@app.get("/orders/get")
def get_orders():
    orders = []

    for order in collection.find():
        order["_id"] = str(order["_id"])
        orders.append(order)

    return orders

@app.put("/orders/{order_id}")
def update_order(order_id:str , order:dict):
    result = collection.update_one(
        {"_id":ObjectId(order_id)},
        {"$set":order}
    )

    return{
        "message":"student updated"
    }

@app.delete("/orders/{orders_id}")
def delete_orders(orders_id:str):
    result =collection.delete_one(
       {"_id": ObjectId(orders_id)}
    )
    return{
        "message":"Orders data deleted"
    }