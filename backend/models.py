"""Database models for recruiter dashboard and ATS integration."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserRole(str, Enum):
    """User roles for RBAC."""

    ADMIN = "admin"
    HIRING_MANAGER = "hiring_manager"
    RECRUITER = "recruiter"


class InterviewStatus(str, Enum):
    """Interview status."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    """User model with role-based access control."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.RECRUITER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    interviews = relationship("Interview", back_populates="recruiter")
    audit_logs = relationship("AuditLog", back_populates="user")


class Candidate(Base):
    """Candidate model synced from ATS."""

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50))
    resume_url = Column(String(500))
    linkedin_url = Column(String(500))
    skills = Column(JSON)
    experience_years = Column(Float)
    education = Column(JSON)
    ats_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    interviews = relationship("Interview", back_populates="candidate")
    scorecards = relationship("Scorecard", back_populates="candidate")


class Interview(Base):
    """Interview session model."""

    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position = Column(String(255), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    status = Column(
        SQLEnum(InterviewStatus), default=InterviewStatus.SCHEDULED, nullable=False
    )
    meeting_link = Column(String(500))
    notes = Column(Text)
    prep_data = Column(JSON)
    live_transcript = Column(Text)
    whisper_suggestions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="interviews")
    recruiter = relationship("User", back_populates="interviews")
    scorecards = relationship("Scorecard", back_populates="interview")
    notifications = relationship("Notification", back_populates="interview")


class Scorecard(Base):
    """Interview scorecard model."""

    __tablename__ = "scorecards"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    technical_score = Column(Float)
    communication_score = Column(Float)
    cultural_fit_score = Column(Float)
    overall_score = Column(Float)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    recommendation = Column(String(50))
    detailed_feedback = Column(Text)
    bias_check_passed = Column(Boolean, default=True)
    bias_flags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    interview = relationship("Interview", back_populates="scorecards")
    candidate = relationship("Candidate", back_populates="scorecards")


class Notification(Base):
    """Notification model for real-time updates."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    interview = relationship("Interview", back_populates="notifications")


class ATSIntegration(Base):
    """ATS integration configuration model."""

    __tablename__ = "ats_integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, index=True, nullable=False)
    api_key_hash = Column(String(255), nullable=False)
    webhook_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Audit log for all dashboard and ATS actions."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    bias_check_result = Column(JSON)
    safety_flags = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")
