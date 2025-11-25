"""Scorecard schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ScorecardBase(BaseModel):
    """Base scorecard schema."""

    technical_score: float = Field(..., ge=0, le=100)
    communication_score: float = Field(..., ge=0, le=100)
    cultural_fit_score: float = Field(..., ge=0, le=100)
    overall_score: float = Field(..., ge=0, le=100)
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    recommendation: str = Field(..., min_length=1, max_length=50)
    detailed_feedback: Optional[str] = None


class ScorecardCreate(ScorecardBase):
    """Scorecard creation schema."""

    interview_id: int
    candidate_id: int

    @field_validator("recommendation")
    @classmethod
    def validate_recommendation(cls, v: str) -> str:
        allowed = ["strongly_recommend", "recommend", "maybe", "not_recommend", "reject"]
        if v.lower() not in allowed:
            raise ValueError(f"recommendation must be one of: {allowed}")
        return v.lower()


class ScorecardUpdate(BaseModel):
    """Scorecard update schema."""

    technical_score: Optional[float] = Field(None, ge=0, le=100)
    communication_score: Optional[float] = Field(None, ge=0, le=100)
    cultural_fit_score: Optional[float] = Field(None, ge=0, le=100)
    overall_score: Optional[float] = Field(None, ge=0, le=100)
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    recommendation: Optional[str] = None
    detailed_feedback: Optional[str] = None


class ScorecardResponse(ScorecardBase):
    """Scorecard response schema."""

    id: int
    interview_id: int
    candidate_id: int
    bias_check_passed: bool
    bias_flags: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScorecardListResponse(BaseModel):
    """Paginated scorecard list response."""

    total: int
    scorecards: list[ScorecardResponse]
    page: int
    page_size: int


class ScorecardExport(BaseModel):
    """Scorecard export format for ATS."""

    candidate_external_id: str
    interview_date: datetime
    position: str
    scores: dict[str, float]
    recommendation: str
    feedback: str
    recruiter_email: str
