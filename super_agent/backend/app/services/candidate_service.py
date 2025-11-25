from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate


class CandidateService:
    """Encapsulates candidate CRUD operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_candidates(self, limit: int = 50, offset: int = 0) -> tuple[list[Candidate], int]:
        query = self.db.query(Candidate).order_by(Candidate.created_at.desc())
        total = query.count()
        items = query.limit(limit).offset(offset).all()
        return items, total

    def get_candidate(self, candidate_id: UUID) -> Candidate | None:
        return self.db.get(Candidate, candidate_id)

    def create_candidate(self, payload: CandidateCreate) -> Candidate:
        candidate = Candidate(**payload.model_dump())
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def update_candidate(self, candidate: Candidate, payload: CandidateUpdate) -> Candidate:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(candidate, field, value)
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate
