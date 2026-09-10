import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent / "utils"))

from query import QueryEngine
from ingestion import run_ingestion
import os

app = FastAPI(title="HDFC Bank Financial RAG")

# Mount web directory
if not os.path.exists("web"):
    os.makedirs("web")
app.mount("/static", StaticFiles(directory="web"), name="static")

query_engine = QueryEngine()

class QueryRequest(BaseModel):
    query: str
    scope: str = "All"

@app.get("/")
async def get_index():
    return FileResponse("web/index.html")

@app.post("/api/query")
async def handle_query(req: QueryRequest):
    try:
        result = query_engine.answer_query(req.query, scope=req.scope)
        return result
    except Exception as e:
        return {
            "answer": f"Error generating answer: {str(e)}",
            "citations": [],
            "raw_context": [],
            "error": str(e),
        }

@app.post("/api/ingest")
async def handle_ingest():
    try:
        run_ingestion()
        return {"status": "success", "message": "PDF ingested successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)