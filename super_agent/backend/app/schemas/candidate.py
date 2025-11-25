from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CandidateBase(BaseModel):
    """Base candidate fields."""

    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    headline: str | None = None
    status: str = "new"
    source: str | None = None
    ats_identifier: str | None = None
    notes: str | None = None
    tags: list[str] | None = None


class CandidateCreate(CandidateBase):
    """Payload for creating a candidate."""


class CandidateUpdate(BaseModel):
    """Payload for updating a candidate."""

    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    headline: str | None = None
    status: str | None = None
    source: str | None = None
    ats_identifier: str | None = None
    notes: str | None = None
    tags: list[str] | None = None


class CandidateResponse(CandidateBase):
    """Response schema for a candidate."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
