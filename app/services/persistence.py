import uuid
from sqlalchemy.orm import Session as DBSession
from app.models.models import User, Session, Answer, Score, RoadmapItem

DEMO_USER_EMAIL = "demo@interview-platform.local"

def get_or_create_demo_user(db: DBSession) -> User:
    """
    For now we use a single demo user so you can test without building login yet.
    Phase 5 replaces this with real auth.
    """
    user = db.query(User).filter(User.email == DEMO_USER_EMAIL).first()
    if not user:
        user = User(
            email=DEMO_USER_EMAIL,
            hashed_password="placeholder",
            full_name="Demo User",
            target_role="Software Engineer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def save_analysis_result(
    db: DBSession,
    question: str,
    transcript: str,
    audio_features: dict,
    nlp_features: dict,
    scores: dict,
    roadmap: list
) -> dict:
    user = get_or_create_demo_user(db)

    # Create a session for this single Q&A
    session = Session(
        user_id=user.id,
        title=f"Practice — {question[:40]}",
        target_role=user.target_role,
        status="completed",
        overall_score=float(scores.get("technical_accuracy", 0)) * 10
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Save the answer with all audio + nlp features, casting NumPy types to standard Python types
    answer = Answer(
        session_id=session.id,
        user_id=user.id,
        question_text=question,
        transcript=transcript,
        duration_secs=int(audio_features.get("duration_secs", 0)),
        speaking_rate_wpm=float(audio_features.get("speaking_rate_wpm", 0)),
        pause_count=int(audio_features.get("pause_count", 0)),
        filler_word_count=int(audio_features.get("filler_word_count", 0)),
        filler_words_raw=audio_features.get("filler_words_breakdown", {}),
        pitch_variance=float(audio_features.get("pitch_variance", 0)),
        avg_pitch_hz=float(audio_features.get("avg_pitch_hz", 0)),
        sentiment_score=float(nlp_features.get("sentiment_score", 0)),
        vocabulary_richness=float(nlp_features.get("vocabulary_richness", 0)),
        coherence_score=float(nlp_features.get("coherence_score", 0)),
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    # Save GPT scores
    composite = round((
        float(scores.get("technical_accuracy", 0)) +
        float(scores.get("completeness", 0)) +
        float(scores.get("clarity", 0)) +
        float(scores.get("depth", 0)) +
        float(scores.get("relevance", 0))
    ) / 5 * 10, 2)

    score_row = Score(
        answer_id=answer.id,
        user_id=user.id,
        technical_accuracy=float(scores.get("technical_accuracy", 0)),
        completeness=float(scores.get("completeness", 0)),
        clarity=float(scores.get("clarity", 0)),
        depth=float(scores.get("depth", 0)),
        relevance=float(scores.get("relevance", 0)),
        composite_score=composite,
        strengths=scores.get("strengths", ""),
        weaknesses=scores.get("weaknesses", ""),
        feedback=scores.get("feedback", ""),
    )
    db.add(score_row)

    # Save roadmap items
    for item in roadmap:
        db.add(RoadmapItem(
            user_id=user.id,
            session_id=session.id,
            title=item.get("title", ""),
            description=item.get("description", ""),
            skill_area=item.get("skill_area", ""),
            priority=item.get("priority", "medium"),
            estimated_hours=float(item.get("estimated_hours", 0)),
        ))

    db.commit()

    return {"session_id": str(session.id), "answer_id": str(answer.id)}