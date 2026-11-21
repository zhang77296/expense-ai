from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="记账AI")

@app.get("/health")
def health():
    return {"msg":"服务正常，访问 /docs 看接口"}

class RecordItem(BaseModel):
    content: str

@app.post("/expenses")
def add_expense(item: RecordItem):
    return {"ok": True, "data": item.dict()}

@app.get("/expenses")
def get_expenses():
    return {"data": []}

@app.post("/budget")
def set_budget():
    return {"ok": True}

@app.get("/budget")
def get_budget():
    return {"budget": 0}

@app.post("/query/ask")
def llm_ask():
    return {"reply": ""}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)