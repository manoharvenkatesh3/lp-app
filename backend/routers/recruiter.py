"""Recruiter dashboard routes."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, WebSocket, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..middleware.audit import log_action
from ..middleware.bias_filter import apply_safety_constraints, validate_scorecard
from ..middleware.rbac import get_current_active_user, require_recruiter
from ..models import Candidate, Interview, InterviewStatus, Scorecard, User
from ..schemas.candidate import CandidateListResponse, CandidateResponse
from ..schemas.interview import (
    InterviewCreate,
    InterviewListResponse,
    InterviewResponse,
    InterviewUpdate,
)
from ..schemas.scorecard import ScorecardCreate, ScorecardResponse
from ..utils.websocket import manager

router = APIRouter(prefix="/recruiter", tags=["recruiter"])


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics."""
    # Count interviews by status
    result = await db.execute(
        select(Interview).where(Interview.recruiter_id == current_user.id)
    )
    interviews = result.scalars().all()
    
    stats = {
        "total_interviews": len(interviews),
        "scheduled": sum(1 for i in interviews if i.status == InterviewStatus.SCHEDULED),
        "in_progress": sum(1 for i in interviews if i.status == InterviewStatus.IN_PROGRESS),
        "completed": sum(1 for i in interviews if i.status == InterviewStatus.COMPLETED),
        "today": sum(
            1
            for i in interviews
            if i.scheduled_at.date() == datetime.utcnow().date()
        ),
    }
    
    await log_action(
        db=db,
        user=current_user,
        action="view_dashboard_stats",
        resource_type="dashboard",
    )
    
    return stats


@router.get("/interviews", response_model=InterviewListResponse)
async def list_interviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[InterviewStatus] = None,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """List interviews for current recruiter."""
    query = select(Interview).where(Interview.recruiter_id == current_user.id)
    
    if status:
        query = query.where(Interview.status == status)
    
    query = query.order_by(Interview.scheduled_at.desc())
    
    # Get total count
    count_query = select(Interview).where(Interview.recruiter_id == current_user.id)
    if status:
        count_query = count_query.where(Interview.status == status)
    
    result = await db.execute(count_query)
    total = len(result.scalars().all())
    
    # Get paginated results
    query = query.limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(query)
    interviews = result.scalars().all()
    
    return {
        "total": total,
        "interviews": interviews,
        "page": page,
        "page_size": page_size,
    }


@router.post("/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate,
    request: Request,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """Schedule a new interview."""
    # Verify candidate exists
    result = await db.execute(
        select(Candidate).where(Candidate.id == interview_data.candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    interview = Interview(
        candidate_id=interview_data.candidate_id,
        recruiter_id=current_user.id,
        position=interview_data.position,
        scheduled_at=interview_data.scheduled_at,
        meeting_link=interview_data.meeting_link,
        notes=interview_data.notes,
        prep_data=interview_data.prep_data,
        status=InterviewStatus.SCHEDULED,
    )
    
    db.add(interview)
    await db.flush()
    
    await log_action(
        db=db,
        user=current_user,
        action="interview_scheduled",
        resource_type="interview",
        resource_id=interview.id,
        details={
            "candidate_id": interview_data.candidate_id,
            "position": interview_data.position,
            "scheduled_at": str(interview_data.scheduled_at),
        },
        request=request,
    )
    
    await db.commit()
    return interview


@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: int,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """Get interview details."""
    result = await db.execute(
        select(Interview).where(
            Interview.id == interview_id,
            Interview.recruiter_id == current_user.id,
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    return interview


@router.patch("/interviews/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: int,
    interview_data: InterviewUpdate,
    request: Request,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """Update interview details."""
    result = await db.execute(
        select(Interview).where(
            Interview.id == interview_id,
            Interview.recruiter_id == current_user.id,
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    update_data = interview_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview, field, value)
    
    await log_action(
        db=db,
        user=current_user,
        action="interview_updated",
        resource_type="interview",
        resource_id=interview.id,
        details=update_data,
        request=request,
    )
    
    await db.commit()
    return interview


@router.post("/scorecards", response_model=ScorecardResponse, status_code=status.HTTP_201_CREATED)
async def create_scorecard(
    scorecard_data: ScorecardCreate,
    request: Request,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """Create an interview scorecard with bias checking."""
    # Verify interview exists and belongs to user
    result = await db.execute(
        select(Interview).where(
            Interview.id == scorecard_data.interview_id,
            Interview.recruiter_id == current_user.id,
        )
    )
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    # Validate for bias
    bias_check = validate_scorecard(scorecard_data.model_dump())
    safety_check = apply_safety_constraints(scorecard_data.model_dump())
    
    scorecard = Scorecard(
        interview_id=scorecard_data.interview_id,
        candidate_id=scorecard_data.candidate_id,
        technical_score=scorecard_data.technical_score,
        communication_score=scorecard_data.communication_score,
        cultural_fit_score=scorecard_data.cultural_fit_score,
        overall_score=scorecard_data.overall_score,
        strengths=scorecard_data.strengths,
        weaknesses=scorecard_data.weaknesses,
        recommendation=scorecard_data.recommendation,
        detailed_feedback=scorecard_data.detailed_feedback,
        bias_check_passed=bias_check["passed"],
        bias_flags=bias_check if not bias_check["passed"] else None,
    )
    
    db.add(scorecard)
    await db.flush()
    
    await log_action(
        db=db,
        user=current_user,
        action="scorecard_created",
        resource_type="scorecard",
        resource_id=scorecard.id,
        details={"interview_id": scorecard_data.interview_id},
        request=request,
        bias_check_result=bias_check,
        safety_flags=safety_check,
    )
    
    await db.commit()
    return scorecard


@router.get("/candidates", response_model=CandidateListResponse)
async def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """List candidates."""
    query = select(Candidate)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Candidate.first_name.ilike(search_pattern))
            | (Candidate.last_name.ilike(search_pattern))
            | (Candidate.email.ilike(search_pattern))
        )
    
    # Get total count
    result = await db.execute(query)
    total = len(result.scalars().all())
    
    # Get paginated results
    query = query.order_by(Candidate.created_at.desc()).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(query)
    candidates = result.scalars().all()
    
    return {
        "total": total,
        "candidates": candidates,
        "page": page,
        "page_size": page_size,
    }


@router.get("/candidates/{candidate_id}/history")
async def get_candidate_history(
    candidate_id: int,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """Get candidate interview history with timeline."""
    result = await db.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # Get interviews
    result = await db.execute(
        select(Interview).where(Interview.candidate_id == candidate_id).order_by(Interview.scheduled_at)
    )
    interviews = result.scalars().all()
    
    # Get scorecards
    result = await db.execute(
        select(Scorecard).where(Scorecard.candidate_id == candidate_id)
    )
    scorecards = result.scalars().all()
    
    timeline = []
    for interview in interviews:
        timeline.append({
            "type": "interview",
            "date": interview.scheduled_at,
            "position": interview.position,
            "status": interview.status.value,
        })
    
    for scorecard in scorecards:
        timeline.append({
            "type": "scorecard",
            "date": scorecard.created_at,
            "overall_score": scorecard.overall_score,
            "recommendation": scorecard.recommendation,
        })
    
    timeline.sort(key=lambda x: x["date"])
    
    return {
        "candidate": CandidateResponse.model_validate(candidate),
        "timeline": timeline,
        "total_interviews": len(interviews),
        "average_score": (
            sum(s.overall_score for s in scorecards) / len(scorecards)
            if scorecards
            else None
        ),
    }


@router.websocket("/ws/interview/{interview_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    interview_id: int,
    db: AsyncSession = Depends(get_db),
):
    """WebSocket endpoint for live interview monitoring."""
    await manager.connect(websocket, interview_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - in production, process and broadcast
            await manager.broadcast_to_interview(
                {"type": "update", "data": data}, interview_id
            )
    except Exception:
        manager.disconnect(websocket, interview_id)
