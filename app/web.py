from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "FIMA AI is running"}


def run_web():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
    )
