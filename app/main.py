from fastapi import FastAPI
from app.database import engine
from app.api.interview import router as interview_router

# 🟢 TARGET THE MODEL DIRECTLY: Import the exact class your app queries
from app.models.models import Session as SessionModel

# Look directly at this model's metadata registry and force-create it in Postgres
print("🛠️ Direct-building tables from SessionModel schema...")
SessionModel.metadata.create_all(bind=engine)
print("✅ Database tables successfully mapped!")

app = FastAPI(title="Interview AI Coach")

# --- If you have any CORS middleware code, keep it right here ---
# app.add_middleware(CORSMiddleware, ...)

app.include_router(interview_router)

@app.get("/")
def root():
    return {"status": "healthy", "message": "Server is up and running!"}
