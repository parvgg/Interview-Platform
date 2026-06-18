from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine
from app.api.interview import router as interview_router
from app.models.models import Session as SessionModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This block runs the exact moment the server starts up
    print("🚀 [STARTUP] Forcing table creation directly from SessionModel...")
    try:
        SessionModel.metadata.create_all(bind=engine)
        print("✅ [STARTUP] Table creation command executed successfully!")
    except Exception as e:
        print(f"❌ [STARTUP] Database table creation failed: {e}")
    yield
    print("🛑 [SHUTDOWN] Server is shutting down...")

# Initialize FastAPI with our monitored lifespan setup
app = FastAPI(title="Interview AI Coach", lifespan=lifespan)

# --- If you have any CORS middleware code, paste it right here ---
# app.add_middleware(CORSMiddleware, ...)

app.include_router(interview_router)

@app.get("/")
def root():
    return {"status": "healthy", "message": "Server is up and running!"}
