import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from google import genai

# We only import the lightweight text-based services now!
from app.services.nlp_analysis import analyze_text
from app.services.scoring import score_answer
from app.services.roadmap import generate_roadmap
from app.services.persistence import save_analysis_result

router = APIRouter(prefix="/api", tags=["interview"])

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def count_filler_words_safe(text: str) -> dict:
    """A lightweight text-based filler word counter that doesn't require heavy audio libraries."""
    fillers = ["um", "uh", "like", "you know", "basically", "literally"]
    text_lower = text.lower().replace(".", "").replace(",", "")
    words = text_lower.split()
    
    breakdown = {}
    total = 0
    
    # Check single words
    for w in words:
        if w in fillers:
            breakdown[w] = breakdown.get(w, 0) + 1
            total += 1
            
    # Check multi-word phrases
    for f in ["you know"]:
        count = text_lower.count(f)
        if count > 0:
            breakdown[f] = breakdown.get(f, 0) + count
            total += count
            
    return {"total": total, "breakdown": breakdown}


@router.post("/analyze")
async def analyze_interview(
    audio: UploadFile = File(...),
    question: str = Form(default="Tell me about yourself."),
    db: DBSession = Depends(get_db)
):
    if not audio.filename.endswith((".wav", ".mp3", ".m4a", ".webm", ".ogg")):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(audio.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    try:
        # 🟢 LAZY RUNTIME FIX: Force table creation out of model metadata on request
        from app.database import engine
        from app.models.models import Session as SessionModel
        SessionModel.metadata.create_all(bind=engine)

        # 1. Cloud-Native Transcription via Gemini (Zero local memory used!)
        print("☁️ Uploading audio to Gemini Cloud...")
        audio_gemini_file = client.files.upload(file=file_path)

        print("📝 Transcribing audio...")
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                audio_gemini_file,
                "Please provide a highly accurate, word-for-word transcript of this audio file. Do not include any explanations or metadata, just the transcript text."
            ]
        )
        transcript = response.text

        # Clean up the file from Google's servers
        try:
            client.files.delete(name=audio_gemini_file.name)
        except Exception as e:
            print(f"Cleanup warning: {e}")

        # 2. Lightweight Audio Features (Bypassing librosa)
        word_count = len(transcript.split())
        duration_estimate = word_count / 2.5  # Rough estimate based on 150 wpm
        filler_data = count_filler_words_safe(transcript)
        
        audio_features = {
            "duration_secs": duration_estimate,
            "speaking_rate_wpm": 150.0, # Safe baseline
            "pause_count": 0,           # Safely disabled for free tier
            "pitch_variance": 0.0,      # Safely disabled for free tier
            "avg_pitch_hz": 0.0,        # Safely disabled for free tier
            "filler_word_count": filler_data["total"],
            "filler_words_breakdown": filler_data["breakdown"]
        }

        # 3. Standard Text Processing
        nlp_features = analyze_text(transcript)
        scores = score_answer(question, transcript)
        roadmap = generate_roadmap(scores, audio_features, nlp_features)

        # 4. Save to PostgreSQL
        saved = save_analysis_result(
            db, question, transcript, audio_features, nlp_features, scores, roadmap
        )

        return {
            "file_id": file_id,
            "session_id": saved["session_id"],
            "question": question,
            "transcript": transcript,
            "audio_features": audio_features,
            "nlp_features": nlp_features,
            "scores": scores,
            "roadmap": roadmap
        }
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/sessions")
def list_sessions(db: DBSession = Depends(get_db)):
    """Get all past sessions for the dashboard."""
    # 🟢 LAZY RUNTIME FIX: Force table creation right before we run the query
    from app.database import engine
    from app.models.models import Session as SessionModel
    SessionModel.metadata.create_all(bind=engine)

    sessions = db.query(SessionModel).order_by(SessionModel.started_at.desc()).all()
    return [
        {
            "id": str(s.id),
            "title": s.title,
            "overall_score": float(s.overall_score) if s.overall_score else 0,
            "started_at": s.started_at.isoformat() if s.started_at else None,
        }
        for s in sessions
    ]
