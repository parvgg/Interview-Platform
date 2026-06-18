from fastapi import FastAPI
from app.api.interview import router as interview_router

import app.models.models
Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI Interview Intelligence Platform")

app.include_router(interview_router)

@app.get("/")
def root():
    return {"status": "AI Interview Platform running"}
