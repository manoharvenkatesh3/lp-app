"""REST API for preinterview pipeline: upload, enrichment, gap analysis, and interview plans."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .enrichment import enrich_candidate_from_sources
from .gap_analysis import analyze_gaps, analyze_multiple_candidates
from .interview_plan import InterviewPlanGenerator
from .models import (
    CandidateProfile,
    EnrichmentRequest,
    EnrichmentResponse,
    GapAnalysisRequest,
    GapAnalysisResult,
    InterviewPlanRequest,
    ResumeParsedResponse,
    ResumeUploadRequest,
)
from .resume_parser import parse_resume

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    logger.info("Preinterview Pipeline API starting up")
    yield
    logger.info("Preinterview Pipeline API shutting down")


# Create FastAPI app
app = FastAPI(
    title="Preinterview Pipeline API",
    description="Resume ingestion, enrichment, gap analysis, and interview plan generation",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "preinterview_pipeline",
    }


# ============================================================================
# Resume Upload & Parsing
# ============================================================================


@app.post(
    "/resume/parse",
    response_model=ResumeParsedResponse,
    tags=["Resume"],
    summary="Parse resume from PDF/DOCX",
    responses={
        400: {"description": "Invalid file format or parsing error"},
        422: {"description": "Validation error"},
    },
)
async def parse_resume_endpoint(
    file: UploadFile = File(..., description="PDF or DOCX resume file"),
    candidate_name: Optional[str] = None,
    candidate_email: Optional[str] = None,
) -> ResumeParsedResponse:
    """
    Parse a resume file (PDF or DOCX) and extract structured candidate profile.

    Args:
        file: Resume file (PDF or DOCX)
        candidate_name: Optional candidate name (used if not found in resume)
        candidate_email: Optional candidate email (used if not found in resume)

    Returns:
        Parsed candidate profile with confidence score and warnings
    """
    # Validate file format
    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a name",
        )

    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ("pdf", "docx", "doc"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported",
        )

    try:
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        # Parse resume
        profile, confidence, warnings = parse_resume(
            file_content=content,
            file_extension=file_ext,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
        )

        return ResumeParsedResponse(
            candidate_profile=profile,
            parsing_confidence=confidence,
            parsing_warnings=warnings,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Resume parsing failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume parsing failed",
        )


# ============================================================================
# Profile Enrichment
# ============================================================================


@app.post(
    "/enrichment/enrich",
    response_model=EnrichmentResponse,
    tags=["Enrichment"],
    summary="Enrich candidate profile with LinkedIn/GitHub data",
    responses={
        400: {"description": "Invalid request"},
        422: {"description": "Validation error"},
    },
)
async def enrich_profile_endpoint(
    request: EnrichmentRequest,
) -> EnrichmentResponse:
    """
    Enrich candidate profile with data from LinkedIn and/or GitHub.

    Args:
        request: Enrichment request with candidate ID and sources

    Returns:
        Enriched profile with enrichment metadata
    """
    try:
        # Note: In production, this would fetch from database
        # For now, we create a minimal profile to enrich
        profile = CandidateProfile(
            candidate_id=request.candidate_id,
            full_name="Candidate",
            email="candidate@example.com",
        )

        # Get GitHub token from environment if available
        github_token = os.getenv("GITHUB_TOKEN")

        # Perform enrichment
        enriched_profile, enrichment_results = await enrich_candidate_from_sources(
            profile=profile,
            sources=request.sources,
            github_token=github_token,
        )

        return EnrichmentResponse(
            candidate_id=request.candidate_id,
            enriched_profile=enriched_profile,
            enrichment_results=enrichment_results,
        )

    except Exception as e:
        logger.exception("Enrichment failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enrichment failed: {str(e)}",
        )


# ============================================================================
# Gap Analysis
# ============================================================================


@app.post(
    "/gap-analysis/analyze",
    response_model=GapAnalysisResult,
    tags=["Gap Analysis"],
    summary="Analyze skill gaps between candidate and job",
    responses={
        400: {"description": "Invalid request"},
        422: {"description": "Validation error"},
    },
)
async def analyze_gaps_endpoint(
    request: GapAnalysisRequest,
) -> GapAnalysisResult:
    """
    Analyze skill gaps between candidate profile and job requirements.

    Args:
        request: Gap analysis request with candidate profile and job spec

    Returns:
        Gap analysis result with critical/significant/minor gaps and strengths
    """
    try:
        # Note: In production, candidate_id would be used to fetch full profile from database
        # For now, we create a minimal profile for the analysis
        candidate_profile = CandidateProfile(
            candidate_id=request.candidate_id,
            full_name="Candidate",
            email="candidate@example.com",
        )

        result = analyze_gaps(
            candidate_profile=candidate_profile,
            job_specification=request.job_specification,
            candidate_id=request.candidate_id,
        )
        return result

    except Exception as e:
        logger.exception("Gap analysis failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gap analysis failed: {str(e)}",
        )


# ============================================================================
# Interview Plan Generation
# ============================================================================


@app.post(
    "/interview-plan/generate",
    tags=["Interview Plan"],
    summary="Generate interview plan based on gap analysis",
    responses={
        400: {"description": "Invalid request"},
        422: {"description": "Validation error"},
    },
)
async def generate_interview_plan_endpoint(
    request: InterviewPlanRequest,
) -> dict:
    """
    Generate a structured interview plan based on gap analysis.

    Args:
        request: Interview plan request with gap analysis and format

    Returns:
        Structured interview plan with questions and guidance
    """
    try:
        generator = InterviewPlanGenerator()
        plan = generator.generate_plan(
            candidate_id=request.candidate_id,
            job_id=request.gap_analysis.job_id,
            gap_analysis=request.gap_analysis,
            interview_format=request.interview_format,
        )

        return plan.model_dump()

    except Exception as e:
        logger.exception("Interview plan generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interview plan generation failed: {str(e)}",
        )


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
