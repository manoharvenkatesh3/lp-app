"""Interview schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from ..models import InterviewStatus


class InterviewBase(BaseModel):
    """Base interview schema."""

    candidate_id: int
    position: str = Field(..., min_length=1, max_length=255)
    scheduled_at: datetime
    meeting_link: Optional[str] = None
    notes: Optional[str] = None


class InterviewCreate(InterviewBase):
    """Interview creation schema."""

    prep_data: Optional[dict[str, Any]] = None


class InterviewUpdate(BaseModel):
    """Interview update schema."""

    position: Optional[str] = Field(None, min_length=1, max_length=255)
    scheduled_at: Optional[datetime] = None
    status: Optional[InterviewStatus] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    live_transcript: Optional[str] = None
    whisper_suggestions: Optional[list[dict[str, Any]]] = None


class InterviewResponse(InterviewBase):
    """Interview response schema."""

    id: int
    recruiter_id: int
    status: InterviewStatus
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    prep_data: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewListResponse(BaseModel):
    """Paginated interview list response."""

    total: int
    interviews: list[InterviewResponse]
    page: int
    page_size: int


class InterviewMonitoringData(BaseModel):
    """Real-time interview monitoring data."""

    interview_id: int
    status: InterviewStatus
    duration_minutes: Optional[int]
    transcript_snippet: Optional[str]
    recent_whispers: list[dict[str, Any]]
    candidate_name: str
    position: str
