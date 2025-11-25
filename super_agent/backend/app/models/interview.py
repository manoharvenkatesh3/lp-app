from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Interview(UUIDMixin, TimestampMixin, Base):
    """Interview lifecycle events and conferencing metadata."""

    __tablename__ = "interviews"

    candidate_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False
    )
    scheduled_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    platform: Mapped[str | None] = mapped_column(String(50))
    meeting_url: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    facilitator: Mapped[str | None] = mapped_column(String(255))
    agenda: Mapped[str | None] = mapped_column(Text())

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="interviews")
    transcripts: Mapped[list["Transcript"]] = relationship(
        "Transcript", back_populates="interview", cascade="all, delete-orphan"
    )
    scorecards: Mapped[list["Scorecard"]] = relationship(
        "Scorecard", back_populates="interview", cascade="all, delete-orphan"
    )
