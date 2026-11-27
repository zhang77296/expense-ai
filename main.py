from fastapi import FastAPI
from pydantic import BaseModel
from query_parser import answer_question
app = FastAPI(title="记账AI")



import os
from dotenv import load_dotenv

load_dotenv()


@app.get("/health")
def health():
    return {"msg":"服务正常，访问 /docs 看接口"}

class RecordItem(BaseModel):
    amount: float
    date: str
    category: str
    merchant: str | None = None
    note: str | None = None

@app.post("/expenses")
def add_expense(item: RecordItem):
    return {"ok": True, "data": item.dict()}

@app.post("/expenses")
def add_expense(item: RecordItem):
    return {"ok": True, "data": item.dict()}

@app.get("/expenses")
def get_expenses():
    import sqlite3
    conn = sqlite3.connect("expense.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses")
    rows = cur.fetchall()
    res = [dict(row) for row in rows]
    conn.close()
    return {"data": res}

@app.post("/budget")
def set_budget():
    return {"ok": True}

@app.get("/budget")
def get_budget():
    return {"budget": 0}

class AskReq(BaseModel):
    question: str

@app.post("/query/ask")
async def ask_question(req: AskReq):
    try:
        result = answer_question(req.question)
        return {"reply": result}
    except Exception as e:
        return {"reply": f"暂时无法处理该查询，错误：{str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
