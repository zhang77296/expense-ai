from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI(title="记账AI")

@app.get("/")
def index():
    return {"msg":"服务正常，访问 /docs 看接口"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)