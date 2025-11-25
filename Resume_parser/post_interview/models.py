"""Data models for post-interview analytics.

This module defines Pydantic models for structured data handling
throughout the post-interview analytics pipeline.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    INTERVIEWER = "interviewer"
    VIEWER = "viewer"


class ScoringAxes(BaseModel):
    """Scoring dimensions for bias-free evaluation."""
    skill_score: float = Field(ge=0, le=100, description="Technical skill assessment")
    clarity_score: float = Field(ge=0, le=100, description="Communication clarity")
    competency_score: float = Field(ge=0, le=100, description="Overall competency")
    
    @validator('*', pre=True)
    def validate_scores(cls, v):
        return max(0, min(100, float(v)))


class StrengthWeakness(BaseModel):
    """Extracted strengths and weaknesses from transcript."""
    strengths: List[str] = Field(default_factory=list, description="Candidate strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Areas for improvement")
    evidence: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Supporting evidence from transcript"
    )


class TranscriptData(BaseModel):
    """Encrypted transcript data structure."""
    session_id: str = Field(description="Unique interview session identifier")
    candidate_id: str = Field(description="Candidate identifier")
    job_id: str = Field(description="Job position identifier")
    interview_type: str = Field(description="Type of interview (technical, behavioral, etc.)")
    duration_minutes: int = Field(ge=0, description="Interview duration in minutes")
    encrypted_content: str = Field(description="PGP/KMS encrypted transcript")
    content_hash: str = Field(description="SHA-256 hash for tamper detection")
    signature: Optional[str] = Field(None, description="Digital signature")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('encrypted_content')
    def validate_encryption(cls, v):
        if not v:
            raise ValueError("Encrypted content cannot be empty")
        return v


class InterviewSession(BaseModel):
    """Complete interview session metadata."""
    session_id: str
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    interviewer_id: str
    interviewer_name: str
    interview_date: datetime
    interview_type: str
    duration_minutes: int
    status: str = Field(default="completed")
    transcript: Optional[TranscriptData] = None


class ScoreCard(BaseModel):
    """Comprehensive scorecard for interview evaluation."""
    session_id: str
    candidate_id: str
    job_id: str
    scoring_axes: ScoringAxes
    overall_score: float = Field(ge=0, le=100)
    job_match_percentage: float = Field(ge=0, le=100)
    strengths_weaknesses: StrengthWeakness
    feedback_narrative: str
    scoring_methodology: Dict[str, Union[str, float, List[str]]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('overall_score')
    def calculate_overall_score(cls, v, values):
        if 'scoring_axes' in values:
            axes = values['scoring_axes']
            return round((axes.skill_score + axes.clarity_score + axes.competency_score) / 3, 2)
        return v


class AnalyticsConfig(BaseModel):
    """Configuration for analytics processing."""
    skill_weight: float = Field(default=0.4, ge=0, le=1)
    clarity_weight: float = Field(default=0.3, ge=0, le=1)
    competency_weight: float = Field(default=0.3, ge=0, le=1)
    
    @validator('*')
    def validate_weights_sum(cls, v, values):
        weights = [values.get('skill_weight', 0), values.get('clarity_weight', 0), 
                  values.get('competency_weight', 0)]
        if sum(weights) != 1.0:
            # Normalize weights to sum to 1.0
            total = sum(weights)
            return v / total
        return v


class AuditLogEntry(BaseModel):
    """Audit log entry for compliance and tracking."""
    log_id: str
    session_id: str
    user_id: str
    user_role: UserRole
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    changes_made: Optional[Dict] = None


class TaskStatus(str, Enum):
    """Background task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class BackgroundTask(BaseModel):
    """Background task metadata."""
    task_id: str
    session_id: str
    task_type: str
    status: TaskStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    result: Optional[Dict] = None