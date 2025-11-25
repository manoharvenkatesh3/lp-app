from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Transcript(UUIDMixin, TimestampMixin, Base):
    """Speech-to-text output with timestamps and speaker labels."""

    __tablename__ = "transcripts"

    interview_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False
    )
    speaker: Mapped[str | None] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text(), nullable=False)
    start_time: Mapped[float | None] = mapped_column(sa.Float)
    end_time: Mapped[float | None] = mapped_column(sa.Float)
    confidence: Mapped[float | None] = mapped_column(sa.Float)

    interview: Mapped["Interview"] = relationship("Interview", back_populates="transcripts")
