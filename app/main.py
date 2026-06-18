from fastapi import FastAPI
from app.database import engine
from app.api.interview import router as interview_router

# 🟢 THE DEFINITIVE FIX: Import the exact Base instance your models live on
from app.models.models import Base

# This ensures every single table registered in your models file is created on boot
print("🛠️ Connecting to cloud database and generating tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables synced successfully!")

app = FastAPI(title="Interview AI Coach")

# --- If you have any CORS middleware code, keep it right here ---
# app.add_middleware(CORSMiddleware, ...)

app.include_router(interview_router)

@app.get("/")
def root():
    return {"status": "healthy", "message": "Server is up and running!"}
