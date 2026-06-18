import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.services.transcription import transcribe_audio
from app.services.audio_analysis import analyze_audio, count_filler_words
from app.services.nlp_analysis import analyze_text
from app.services.scoring import score_answer
from app.services.roadmap import generate_roadmap
from app.services.persistence import save_analysis_result

router = APIRouter(prefix="/api", tags=["interview"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
        transcript = transcribe_audio(file_path)

        audio_features = analyze_audio(file_path)
        filler_data = count_filler_words(transcript)
        audio_features["filler_word_count"] = filler_data["total"]
        audio_features["filler_words_breakdown"] = filler_data["breakdown"]

        nlp_features = analyze_text(transcript)
        scores = score_answer(question, transcript)
        roadmap = generate_roadmap(scores, audio_features, nlp_features)

        # Save everything to PostgreSQL
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
    from app.models.models import Session as SessionModel
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