"""Candidate schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class CandidateBase(BaseModel):
    """Base candidate schema."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: Optional[list[str]] = None
    experience_years: Optional[float] = None
    education: Optional[list[dict[str, Any]]] = None


class CandidateCreate(CandidateBase):
    """Candidate creation schema."""

    external_id: Optional[str] = None
    ats_data: Optional[dict[str, Any]] = None


class CandidateUpdate(BaseModel):
    """Candidate update schema."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: Optional[list[str]] = None
    experience_years: Optional[float] = None
    education: Optional[list[dict[str, Any]]] = None
    ats_data: Optional[dict[str, Any]] = None


class CandidateResponse(CandidateBase):
    """Candidate response schema."""

    id: int
    external_id: Optional[str]
    ats_data: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    """Paginated candidate list response."""

    total: int
    candidates: list[CandidateResponse]
    page: int
    page_size: int
