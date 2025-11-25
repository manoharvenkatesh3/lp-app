from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_candidate_service
from app.schemas.candidate import CandidateCreate, CandidateResponse, CandidateUpdate
from app.services.candidate_service import CandidateService

router = APIRouter()


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    payload: CandidateCreate,
    service: CandidateService = Depends(get_candidate_service),
) -> CandidateResponse:
    """Create a new candidate."""

    candidate = service.create_candidate(payload)
    return CandidateResponse.model_validate(candidate)


@router.get("", response_model=list[CandidateResponse])
def list_candidates(
    limit: int = 50,
    offset: int = 0,
    service: CandidateService = Depends(get_candidate_service),
) -> list[CandidateResponse]:
    """List candidates with pagination."""

    items, _ = service.list_candidates(limit=limit, offset=offset)
    return [CandidateResponse.model_validate(c) for c in items]


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: UUID,
    service: CandidateService = Depends(get_candidate_service),
) -> CandidateResponse:
    """Get a candidate by ID."""

    candidate = service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return CandidateResponse.model_validate(candidate)


@router.patch("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: UUID,
    payload: CandidateUpdate,
    service: CandidateService = Depends(get_candidate_service),
) -> CandidateResponse:
    """Update a candidate."""

    candidate = service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    updated = service.update_candidate(candidate, payload)
    return CandidateResponse.model_validate(updated)
