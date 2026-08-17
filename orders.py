from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Order(BaseModel):
    id: int
    item: str
    quantity: int

# simple in-memory store for demo purposes
_orders = {
    1: {"id": 1, "item": "apple", "quantity": 3},
    2: {"id": 2, "item": "banana", "quantity": 5},
}

@router.get("/", response_model=List[Order])
def list_orders():
    return list(_orders.values())

@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int):
    order = _orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=Order, status_code=201)
def create_order(order: Order):
    if order.id in _orders:
        raise HTTPException(status_code=400, detail="Order already exists")
    _orders[order.id] = order.dict()
    return order
