from __future__ import annotations

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Scorecard(UUIDMixin, TimestampMixin, Base):
    """Evaluation rubric and reviewer feedback."""

    __tablename__ = "scorecards"

    candidate_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False
    )
    interview_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interviews.id", ondelete="SET NULL")
    )
    reviewer: Mapped[str | None] = mapped_column(String(255))
    overall_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    decision: Mapped[str | None] = mapped_column(String(50))
    feedback: Mapped[str | None] = mapped_column(Text())
    rubric: Mapped[str | None] = mapped_column(Text())

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="scorecards")
    interview: Mapped["Interview" | None] = relationship("Interview", back_populates="scorecards")
