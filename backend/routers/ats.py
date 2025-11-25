"""ATS integration routes."""
from __future__ import annotations

import secrets
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..middleware.audit import log_action
from ..middleware.bias_filter import check_for_bias, sanitize_feedback
from ..middleware.rate_limit import ats_rate_limit_dependency
from ..models import ATSIntegration, Candidate, Interview, Scorecard, User
from ..schemas.candidate import CandidateCreate, CandidateListResponse, CandidateResponse
from ..schemas.scorecard import ScorecardExport
from ..utils.jwt import get_password_hash

router = APIRouter(prefix="/ats", tags=["ats"])


async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> ATSIntegration:
    """Verify ATS API key."""
    result = await db.execute(
        select(ATSIntegration).where(
            ATSIntegration.api_key == x_api_key,
            ATSIntegration.is_active == True,
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return integration


@router.post(
    "/candidates/sync",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ats_rate_limit_dependency)],
)
async def sync_candidate(
    candidate_data: CandidateCreate,
    request: Request,
    integration: ATSIntegration = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync a candidate from ATS.
    
    This endpoint allows ATS systems to push candidate data to the platform.
    """
    # Check if candidate already exists
    if candidate_data.external_id:
        result = await db.execute(
            select(Candidate).where(Candidate.external_id == candidate_data.external_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing candidate
            for field, value in candidate_data.model_dump(exclude_unset=True).items():
                setattr(existing, field, value)
            candidate = existing
        else:
            # Create new candidate
            candidate = Candidate(**candidate_data.model_dump())
            db.add(candidate)
    else:
        candidate = Candidate(**candidate_data.model_dump())
        db.add(candidate)
    
    await db.flush()
    
    await log_action(
        db=db,
        user=None,
        action="ats_candidate_sync",
        resource_type="candidate",
        resource_id=candidate.id,
        details={
            "ats_integration": integration.name,
            "external_id": candidate_data.external_id,
        },
        request=request,
    )
    
    await db.commit()
    return candidate


@router.get(
    "/candidates",
    response_model=CandidateListResponse,
    dependencies=[Depends(ats_rate_limit_dependency)],
)
async def get_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    updated_since: Optional[datetime] = None,
    integration: ATSIntegration = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve candidates for ATS sync.
    
    Supports filtering by last update time for incremental sync.
    """
    query = select(Candidate)
    
    if updated_since:
        query = query.where(Candidate.updated_at >= updated_since)
    
    # Get total count
    result = await db.execute(query)
    total = len(result.scalars().all())
    
    # Get paginated results
    query = query.order_by(Candidate.updated_at.desc()).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(query)
    candidates = result.scalars().all()
    
    await log_action(
        db=db,
        user=None,
        action="ats_candidates_retrieved",
        resource_type="candidate",
        details={
            "ats_integration": integration.name,
            "count": len(candidates),
        },
    )
    
    return {
        "total": total,
        "candidates": candidates,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/scorecards/export",
    response_model=list[ScorecardExport],
    dependencies=[Depends(ats_rate_limit_dependency)],
)
async def export_scorecards(
    candidate_external_id: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    integration: ATSIntegration = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Export scorecards to ATS.
    
    Supports filtering by candidate and date range.
    Includes bias-filtered feedback.
    """
    query = select(Scorecard, Interview, Candidate, User).join(
        Interview, Scorecard.interview_id == Interview.id
    ).join(
        Candidate, Scorecard.candidate_id == Candidate.id
    ).join(
        User, Interview.recruiter_id == User.id
    )
    
    if candidate_external_id:
        query = query.where(Candidate.external_id == candidate_external_id)
    
    if from_date:
        query = query.where(Scorecard.created_at >= from_date)
    
    if to_date:
        query = query.where(Scorecard.created_at <= to_date)
    
    result = await db.execute(query)
    rows = result.all()
    
    exports = []
    for scorecard, interview, candidate, recruiter in rows:
        # Apply bias filtering to feedback
        sanitized_feedback = sanitize_feedback(
            scorecard.detailed_feedback or ""
        )
        
        # Check if feedback still has bias issues
        bias_check = check_for_bias(sanitized_feedback)
        if not bias_check["passed"]:
            # Add warning to feedback
            sanitized_feedback = (
                f"[Content filtered for bias] {sanitized_feedback}"
            )
        
        exports.append(
            ScorecardExport(
                candidate_external_id=candidate.external_id or str(candidate.id),
                interview_date=interview.scheduled_at,
                position=interview.position,
                scores={
                    "technical": scorecard.technical_score,
                    "communication": scorecard.communication_score,
                    "cultural_fit": scorecard.cultural_fit_score,
                    "overall": scorecard.overall_score,
                },
                recommendation=scorecard.recommendation,
                feedback=sanitized_feedback,
                recruiter_email=recruiter.email,
            )
        )
    
    await log_action(
        db=db,
        user=None,
        action="ats_scorecards_exported",
        resource_type="scorecard",
        details={
            "ats_integration": integration.name,
            "count": len(exports),
        },
    )
    
    return exports


@router.post(
    "/feedback/sync",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ats_rate_limit_dependency)],
)
async def sync_feedback(
    candidate_external_id: str,
    feedback_data: dict,
    request: Request,
    integration: ATSIntegration = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync feedback from ATS.
    
    Allows ATS systems to push additional feedback or notes.
    """
    # Find candidate
    result = await db.execute(
        select(Candidate).where(Candidate.external_id == candidate_external_id)
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # Check feedback for bias
    feedback_text = feedback_data.get("text", "")
    bias_check = check_for_bias(feedback_text)
    
    if not bias_check["passed"]:
        # Sanitize feedback
        feedback_data["text"] = sanitize_feedback(feedback_text)
        feedback_data["bias_filtered"] = True
    
    # Update candidate's ATS data
    if not candidate.ats_data:
        candidate.ats_data = {}
    
    if "feedback" not in candidate.ats_data:
        candidate.ats_data["feedback"] = []
    
    candidate.ats_data["feedback"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "source": integration.name,
        "data": feedback_data,
    })
    
    await log_action(
        db=db,
        user=None,
        action="ats_feedback_synced",
        resource_type="candidate",
        resource_id=candidate.id,
        details={
            "ats_integration": integration.name,
            "external_id": candidate_external_id,
        },
        request=request,
        bias_check_result=bias_check,
    )
    
    await db.commit()
    
    return {
        "status": "success",
        "candidate_id": candidate.id,
        "bias_filtered": not bias_check["passed"],
    }


@router.post("/integrations/register", status_code=status.HTTP_201_CREATED)
async def register_ats_integration(
    name: str,
    webhook_url: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new ATS integration.
    
    Returns an API key for authentication.
    Note: This endpoint should be protected in production.
    """
    # Generate API key
    api_key = f"ats_{secrets.token_urlsafe(32)}"
    api_key_hash = get_password_hash(api_key)
    
    integration = ATSIntegration(
        name=name,
        api_key=api_key,
        api_key_hash=api_key_hash,
        webhook_url=webhook_url,
        is_active=True,
    )
    
    db.add(integration)
    await db.commit()
    
    return {
        "integration_id": integration.id,
        "name": integration.name,
        "api_key": api_key,
        "message": "Store this API key securely. It cannot be retrieved again.",
    }
