from fastapi import FastAPI
from pydantic import BaseModel
from query_parser import answer_question

app = FastAPI(title="记账项目接口")

class AskReq(BaseModel):
    question: str

@app.post("/query/ask")
async def ask_question(req: AskReq):
    result = answer_question(req.question)
    return {"reply": result}