from fastapi import FastAPI
from app.database import engine
from app.api.interview import router as interview_router

# 🟢 THE BULLETPROOF FIX: Import the actual model class directly
from app.models.models import Session as SessionModel

# Bind the engine directly to the model's own metadata registry.
# This completely bypasses any "duplicate Base class" confusion!
SessionModel.metadata.create_all(bind=engine)

app = FastAPI(title="Interview AI Coach")

# --- If you have any CORS middleware code, keep it right here ---
# app.add_middleware(CORSMiddleware, ...)

app.include_router(interview_router)

@app.get("/")
def root():
    return {"status": "healthy", "message": "Server is up and running!"}
