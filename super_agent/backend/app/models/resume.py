from __future__ import annotations

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Resume(UUIDMixin, TimestampMixin, Base):
    """Resume document metadata and parsed content."""

    __tablename__ = "resumes"

    candidate_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(512))
    parsed_text: Mapped[str | None] = mapped_column(Text())
    structured_data: Mapped[str | None] = mapped_column(Text())

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="resumes")
