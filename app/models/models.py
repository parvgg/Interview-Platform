import uuid
from sqlalchemy import Column, String, Integer, SmallInteger, Numeric, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150))
    target_role = Column(String(150))
    created_at = Column(TIMESTAMP, server_default=func.now())


class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200))
    target_role = Column(String(150))
    status = Column(String(20), default="completed")
    started_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP)
    overall_score = Column(Numeric(5, 2))


class Answer(Base):
    __tablename__ = "answers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text)
    transcript = Column(Text)
    duration_secs = Column(SmallInteger)
    speaking_rate_wpm = Column(Numeric(6, 2))
    pause_count = Column(SmallInteger)
    filler_word_count = Column(SmallInteger)
    filler_words_raw = Column(JSON)
    pitch_variance = Column(Numeric(8, 4))
    avg_pitch_hz = Column(Numeric(8, 4))
    sentiment_score = Column(Numeric(4, 3))
    vocabulary_richness = Column(Numeric(4, 3))
    coherence_score = Column(Numeric(4, 3))
    submitted_at = Column(TIMESTAMP, server_default=func.now())


class Score(Base):
    __tablename__ = "scores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    answer_id = Column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    technical_accuracy = Column(Numeric(4, 2))
    completeness = Column(Numeric(4, 2))
    clarity = Column(Numeric(4, 2))
    depth = Column(Numeric(4, 2))
    relevance = Column(Numeric(4, 2))
    composite_score = Column(Numeric(5, 2))
    strengths = Column(Text)
    weaknesses = Column(Text)
    feedback = Column(Text)
    scored_at = Column(TIMESTAMP, server_default=func.now())


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    skill_area = Column(String(100))
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="pending")
    estimated_hours = Column(Numeric(4, 1))
    created_at = Column(TIMESTAMP, server_default=func.now())