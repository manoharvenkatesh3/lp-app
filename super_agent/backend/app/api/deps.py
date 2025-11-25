from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.candidate_service import CandidateService


def get_candidate_service(db: Session = Depends(get_db)) -> CandidateService:
    """Dependency injector for CandidateService."""

    return CandidateService(db)
