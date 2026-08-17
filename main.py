from fastapi import FastAPI
from orders import router as orders_router

app = FastAPI()

# include orders router at /orders
app.include_router(orders_router, prefix="/orders")

@app.get("/")
def read_root():
    return {"message": "Hello from uvicorn"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
