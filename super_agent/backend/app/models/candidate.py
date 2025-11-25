from __future__ import annotations

from typing import List

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Candidate(UUIDMixin, TimestampMixin, Base):
    """Candidate metadata and ATS sync state."""

    __tablename__ = "candidates"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(32))
    headline: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="new")
    source: Mapped[str | None] = mapped_column(String(50))
    ats_identifier: Mapped[str | None] = mapped_column(String(128), unique=True)
    notes: Mapped[str | None] = mapped_column(Text())
    tags: Mapped[List[str] | None] = mapped_column(ARRAY(String(64)))

    resumes: Mapped[list["Resume"]] = relationship(
        "Resume", back_populates="candidate", cascade="all, delete-orphan"
    )
    interviews: Mapped[list["Interview"]] = relationship(
        "Interview", back_populates="candidate", cascade="all, delete-orphan"
    )
    scorecards: Mapped[list["Scorecard"]] = relationship(
        "Scorecard", back_populates="candidate", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="candidate", cascade="all, delete-orphan"
    )
