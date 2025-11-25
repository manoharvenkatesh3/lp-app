"""Data models for candidate profiles, enrichment, gap analysis, and interview plans."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SkillLevel(str, Enum):
    """Proficiency levels for skills."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ProfessionalExperience(BaseModel):
    """A professional work experience entry."""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM or YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM or YYYY-MM-DD)")
    duration_months: Optional[int] = Field(None, description="Duration in months")
    description: Optional[str] = Field(None, description="Job description and responsibilities")
    location: Optional[str] = Field(None, description="Job location")


class Skill(BaseModel):
    """A candidate skill with proficiency level."""

    name: str = Field(..., description="Skill name")
    level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE, description="Proficiency level")
    years_experience: Optional[float] = Field(None, description="Years of experience with this skill")
    endorsements: Optional[int] = Field(None, description="Number of endorsements/validations")


class Education(BaseModel):
    """Educational background entry."""

    degree: str = Field(..., description="Degree type (e.g., Bachelor's, Master's)")
    field_of_study: str = Field(..., description="Field of study")
    institution: str = Field(..., description="School/University name")
    graduation_date: Optional[str] = Field(None, description="Graduation date (YYYY or YYYY-MM)")
    gpa: Optional[float] = Field(None, description="GPA if available")


class LinkedInProfile(BaseModel):
    """LinkedIn profile enrichment data."""

    profile_url: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    headline: Optional[str] = Field(None, description="LinkedIn headline")
    summary: Optional[str] = Field(None, description="LinkedIn profile summary")
    endorsement_count: Optional[int] = Field(None, description="Total endorsements")
    connection_count: Optional[int] = Field(None, description="Number of connections")
    verified: bool = Field(default=False, description="Whether profile was verified")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


class GitHubProfile(BaseModel):
    """GitHub profile enrichment data."""

    github_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    username: Optional[str] = Field(None, description="GitHub username")
    public_repos: Optional[int] = Field(None, description="Number of public repositories")
    followers: Optional[int] = Field(None, description="Number of followers")
    bio: Optional[str] = Field(None, description="GitHub bio")
    verified: bool = Field(default=False, description="Whether profile was verified")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


class EnrichmentMetadata(BaseModel):
    """Metadata about data enrichment process."""

    source: str = Field(..., description="Source of enrichment (e.g., 'linkedin', 'github')")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When enrichment occurred")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score 0-1")
    provenance: Optional[str] = Field(None, description="Audit trail: how data was obtained")


class CandidateProfile(BaseModel):
    """Normalized candidate profile schema."""

    candidate_id: Optional[str] = Field(None, description="Unique candidate identifier")
    full_name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Current location")

    # Professional background
    current_title: Optional[str] = Field(None, description="Current job title")
    total_experience_years: float = Field(default=0.0, description="Total years of experience")
    experiences: List[ProfessionalExperience] = Field(default_factory=list, description="Work history")

    # Skills and education
    skills: List[Skill] = Field(default_factory=list, description="List of skills")
    education: List[Education] = Field(default_factory=list, description="Educational background")

    # URLs and contacts
    linkedin_profile: Optional[LinkedInProfile] = Field(None, description="LinkedIn data")
    github_profile: Optional[GitHubProfile] = Field(None, description="GitHub data")
    portfolio_url: Optional[HttpUrl] = Field(None, description="Portfolio website URL")

    # Raw data
    raw_cv_content: Optional[str] = Field(None, description="Raw CV/resume text content")
    cv_file_hash: Optional[str] = Field(None, description="Hash of uploaded CV file for deduplication")

    # Enrichment tracking
    enrichment_metadata: List[EnrichmentMetadata] = Field(
        default_factory=list, description="History of enrichment operations"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Profile creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = ConfigDict(use_enum_values=False)


class JobRequirement(BaseModel):
    """A single job requirement/skill needed."""

    name: str = Field(..., description="Requirement name")
    category: str = Field(default="technical", description="Category: technical, soft, domain, etc.")
    level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE, description="Required proficiency level")
    importance: float = Field(default=1.0, ge=0.0, le=1.0, description="Importance weight 0-1")
    nice_to_have: bool = Field(default=False, description="Whether this is nice-to-have vs required")


class JobSpecification(BaseModel):
    """Job specification for gap analysis."""

    job_id: Optional[str] = Field(None, description="Unique job identifier")
    job_title: str = Field(..., description="Job title")
    job_description: str = Field(..., description="Full job description")
    requirements: List[JobRequirement] = Field(default_factory=list, description="Specific requirements")
    min_experience_years: float = Field(default=0.0, description="Minimum years of experience")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skill list")
    nice_to_have_skills: List[str] = Field(default_factory=list, description="Nice-to-have skills")


class SkillGap(BaseModel):
    """A skill gap between candidate and job requirement."""

    skill_name: str = Field(..., description="Skill name")
    required_level: SkillLevel = Field(..., description="Required proficiency level")
    candidate_level: Optional[SkillLevel] = Field(None, description="Candidate's current level")
    gap_severity: str = Field(..., description="'critical', 'significant', 'minor', or 'none'")
    importance: float = Field(ge=0.0, le=1.0, description="How important this gap is")
    learning_path: Optional[str] = Field(None, description="Suggested learning path to close gap")


class GapAnalysisResult(BaseModel):
    """Results of skill gap analysis."""

    candidate_id: str = Field(..., description="Candidate ID")
    job_id: str = Field(..., description="Job ID")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Gaps and strengths
    critical_gaps: List[SkillGap] = Field(default_factory=list, description="Critical skill gaps")
    significant_gaps: List[SkillGap] = Field(default_factory=list, description="Significant gaps")
    minor_gaps: List[SkillGap] = Field(default_factory=list, description="Minor gaps")
    strengths: List[str] = Field(default_factory=list, description="Candidate's strengths vs job")

    # Overall assessment
    overall_fit_score: float = Field(ge=0.0, le=100.0, description="Overall fit percentage 0-100")
    readiness_level: str = Field(..., description="'ready', 'trainable', 'consider', 'not_suitable'")
    summary: str = Field(..., description="Human-readable summary of gap analysis")


class InterviewQuestion(BaseModel):
    """A single interview question."""

    question_id: str = Field(..., description="Unique question ID")
    question_text: str = Field(..., description="The actual question to ask")
    competency: str = Field(..., description="Which competency/gap this targets")
    question_type: str = Field(
        default="open_ended", description="Type: open_ended, behavioral, technical, scenario"
    )
    difficulty: str = Field(default="medium", description="Difficulty level: easy, medium, hard")
    follow_ups: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    evaluation_criteria: Optional[str] = Field(None, description="How to evaluate the response")


class InterviewPlan(BaseModel):
    """Structured interview plan for a candidate-job pairing."""

    plan_id: Optional[str] = Field(None, description="Unique plan identifier")
    candidate_id: str = Field(..., description="Candidate ID")
    job_id: str = Field(..., description="Job ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Plan creation timestamp")

    # Interview structure
    interview_focus: str = Field(..., description="Primary focus of interview")
    interview_duration_minutes: int = Field(default=60, description="Recommended duration")
    interviewer_notes: Optional[str] = Field(None, description="Notes for the interviewer")

    # Questions organized by competency
    competency_focus: List[str] = Field(..., description="Key competencies to assess")
    questions: List[InterviewQuestion] = Field(..., description="Interview questions")

    # Gap-specific guidance
    critical_gap_exploration: Optional[str] = Field(
        None, description="How to explore critical gaps during interview"
    )
    strength_validation: Optional[str] = Field(None, description="How to validate strengths")
    risk_indicators: List[str] = Field(default_factory=list, description="Red flags to watch for")

    model_config = ConfigDict(use_enum_values=False)


class ResumeUploadRequest(BaseModel):
    """Request model for resume upload."""

    candidate_name: Optional[str] = Field(None, description="Candidate name (optional, can be parsed)")
    candidate_email: Optional[str] = Field(None, description="Candidate email (optional)")


class ResumeParsedResponse(BaseModel):
    """Response from resume parsing."""

    candidate_profile: CandidateProfile = Field(..., description="Parsed candidate profile")
    parsing_confidence: float = Field(ge=0.0, le=1.0, description="Confidence of parsing 0-1")
    parsing_warnings: List[str] = Field(default_factory=list, description="Any warnings during parsing")


class EnrichmentRequest(BaseModel):
    """Request model for profile enrichment."""

    candidate_id: str = Field(..., description="Candidate ID to enrich")
    sources: List[str] = Field(default=["linkedin", "github"], description="Sources to enrich from")
    update_existing: bool = Field(default=False, description="Update existing enrichment data")


class EnrichmentResponse(BaseModel):
    """Response from enrichment operation."""

    candidate_id: str = Field(..., description="Candidate ID")
    enriched_profile: CandidateProfile = Field(..., description="Updated candidate profile")
    enrichment_results: dict = Field(..., description="Detailed enrichment results")


class GapAnalysisRequest(BaseModel):
    """Request for gap analysis."""

    candidate_id: str = Field(..., description="Candidate ID")
    job_specification: JobSpecification = Field(..., description="Job specification")


class InterviewPlanRequest(BaseModel):
    """Request for interview plan generation."""

    candidate_id: str = Field(..., description="Candidate ID")
    gap_analysis: GapAnalysisResult = Field(..., description="Gap analysis results")
    interview_format: str = Field(
        default="full_loop", description="Format: phone_screen, technical, full_loop, executive"
    )
