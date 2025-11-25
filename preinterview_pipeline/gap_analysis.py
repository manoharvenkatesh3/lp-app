"""Skill gap analysis engine comparing candidate profiles against job specifications."""
from __future__ import annotations

import logging
from typing import Optional

from .models import (
    CandidateProfile,
    GapAnalysisResult,
    JobRequirement,
    JobSpecification,
    SkillGap,
    SkillLevel,
)

logger = logging.getLogger(__name__)

# Gap severity thresholds
GAP_SEVERITY_THRESHOLDS = {
    "critical": 0.2,  # Less than 20% match
    "significant": 0.5,  # 20-50% match
    "minor": 0.8,  # 50-80% match
    "none": 1.0,  # 80%+ match
}


def normalize_skill_name(skill: str) -> str:
    """Normalize skill name for comparison."""
    return skill.lower().strip()


def find_candidate_skill(profile: CandidateProfile, skill_name: str) -> Optional[object]:
    """Find a skill in candidate profile by name."""
    normalized_target = normalize_skill_name(skill_name)
    for skill in profile.skills:
        if normalize_skill_name(skill.name) == normalized_target:
            return skill
    return None


def calculate_skill_match(candidate_level: Optional[SkillLevel], required_level: SkillLevel) -> float:
    """
    Calculate skill match score 0-1.

    Args:
        candidate_level: Candidate's proficiency level (None if skill missing)
        required_level: Required proficiency level

    Returns:
        Match score 0-1
    """
    if candidate_level is None:
        return 0.0  # No skill

    level_rankings = {
        SkillLevel.BEGINNER: 1,
        SkillLevel.INTERMEDIATE: 2,
        SkillLevel.ADVANCED: 3,
        SkillLevel.EXPERT: 4,
    }

    candidate_rank = level_rankings.get(candidate_level, 0)
    required_rank = level_rankings.get(required_level, 0)

    if required_rank == 0:
        return 0.0

    # Scale: candidate_rank / required_rank, capped at 1.0
    return min(1.0, candidate_rank / required_rank)


def classify_gap_severity(match_score: float) -> str:
    """Classify gap severity based on match score."""
    if match_score >= GAP_SEVERITY_THRESHOLDS["none"]:
        return "none"
    if match_score >= GAP_SEVERITY_THRESHOLDS["minor"]:
        return "minor"
    if match_score >= GAP_SEVERITY_THRESHOLDS["significant"]:
        return "significant"
    return "critical"


def analyze_gaps(
    candidate_profile: CandidateProfile,
    job_specification: JobSpecification,
    candidate_id: Optional[str] = None,
    job_id: Optional[str] = None,
) -> GapAnalysisResult:
    """
    Analyze skill gaps between candidate and job requirements.

    Args:
        candidate_profile: Candidate profile
        job_specification: Job specification with requirements
        candidate_id: Optional candidate ID
        job_id: Optional job ID

    Returns:
        Gap analysis result
    """
    candidate_id = candidate_id or candidate_profile.candidate_id or "unknown"
    job_id = job_id or job_specification.job_id or "unknown"

    critical_gaps: list[SkillGap] = []
    significant_gaps: list[SkillGap] = []
    minor_gaps: list[SkillGap] = []
    strengths: list[str] = []

    total_fit_score = 0.0
    gap_count = 0

    # Analyze each job requirement
    for requirement in job_specification.requirements:
        candidate_skill = find_candidate_skill(candidate_profile, requirement.name)
        candidate_level = candidate_skill.level if candidate_skill else None

        match_score = calculate_skill_match(candidate_level, requirement.level)
        gap_severity = classify_gap_severity(match_score)

        # Adjust by importance
        weighted_score = match_score * requirement.importance

        if gap_severity == "none":
            strengths.append(f"{requirement.name} (experienced)")
        else:
            gap = SkillGap(
                skill_name=requirement.name,
                required_level=requirement.level,
                candidate_level=candidate_level,
                gap_severity=gap_severity,
                importance=requirement.importance,
                learning_path=_suggest_learning_path(requirement.name, requirement.level),
            )

            if gap_severity == "critical":
                critical_gaps.append(gap)
            elif gap_severity == "significant":
                significant_gaps.append(gap)
            else:  # minor
                minor_gaps.append(gap)

        total_fit_score += weighted_score
        gap_count += 1

    # Also check for nice-to-have skills that candidate has (strengths)
    for skill in candidate_profile.skills:
        if skill.name in job_specification.nice_to_have_skills:
            strengths.append(f"{skill.name} (bonus)")

    # Calculate overall fit score
    overall_fit_score = (total_fit_score / max(1, gap_count)) * 100

    # Determine readiness level
    readiness_level = _classify_readiness(
        critical_gaps=len(critical_gaps),
        significant_gaps=len(significant_gaps),
        overall_fit_score=overall_fit_score,
        total_requirements=len(job_specification.requirements),
    )

    # Generate summary
    summary = _generate_gap_summary(
        critical_gaps=critical_gaps,
        significant_gaps=significant_gaps,
        overall_fit_score=overall_fit_score,
        readiness_level=readiness_level,
        strengths=strengths,
    )

    return GapAnalysisResult(
        candidate_id=str(candidate_id),
        job_id=str(job_id),
        critical_gaps=critical_gaps,
        significant_gaps=significant_gaps,
        minor_gaps=minor_gaps,
        strengths=strengths,
        overall_fit_score=round(overall_fit_score, 1),
        readiness_level=readiness_level,
        summary=summary,
    )


def _suggest_learning_path(skill_name: str, required_level: SkillLevel) -> str:
    """Suggest a learning path to close a skill gap."""
    level_suggestions = {
        SkillLevel.BEGINNER: "Take introductory courses and tutorials",
        SkillLevel.INTERMEDIATE: "Build practice projects and complete hands-on labs",
        SkillLevel.ADVANCED: "Lead technical projects and mentoring others",
        SkillLevel.EXPERT: "Contribute to open source or publish research",
    }
    return level_suggestions.get(required_level, "Practice and professional development")


def _classify_readiness(
    critical_gaps: int,
    significant_gaps: int,
    overall_fit_score: float,
    total_requirements: int,
) -> str:
    """
    Classify candidate readiness for the role.

    Returns:
        'ready', 'trainable', 'consider', or 'not_suitable'
    """
    if critical_gaps > 0 and critical_gaps > total_requirements * 0.3:
        return "not_suitable"

    if overall_fit_score >= 85:
        return "ready"

    if overall_fit_score >= 70 and significant_gaps <= total_requirements * 0.3:
        return "trainable"

    if overall_fit_score >= 60:
        return "consider"

    return "not_suitable"


def _generate_gap_summary(
    critical_gaps: list[SkillGap],
    significant_gaps: list[SkillGap],
    overall_fit_score: float,
    readiness_level: str,
    strengths: list[str],
) -> str:
    """Generate a human-readable summary of gap analysis."""
    summary_parts = []

    # Overall assessment
    if readiness_level == "ready":
        summary_parts.append(f"Candidate is ready for the role ({overall_fit_score:.1f}% fit).")
    elif readiness_level == "trainable":
        summary_parts.append(
            f"Candidate is trainable with some development ({overall_fit_score:.1f}% current fit)."
        )
    elif readiness_level == "consider":
        summary_parts.append(
            f"Candidate should be considered with reservations ({overall_fit_score:.1f}% fit)."
        )
    else:
        summary_parts.append(
            f"Candidate is not well-suited for this role ({overall_fit_score:.1f}% fit)."
        )

    # Critical gaps
    if critical_gaps:
        gap_list = ", ".join(g.skill_name for g in critical_gaps[:3])
        plural = "gaps" if len(critical_gaps) > 1 else "gap"
        summary_parts.append(f"Critical {plural}: {gap_list}")
        if len(critical_gaps) > 3:
            summary_parts.append(f"...and {len(critical_gaps) - 3} more")

    # Significant gaps
    if significant_gaps:
        gap_list = ", ".join(g.skill_name for g in significant_gaps[:2])
        plural = "gaps" if len(significant_gaps) > 1 else "gap"
        summary_parts.append(f"Significant {plural}: {gap_list}")

    # Strengths
    if strengths:
        strength_list = ", ".join(strengths[:3])
        summary_parts.append(f"Strengths: {strength_list}")

    return " ".join(summary_parts)


def analyze_multiple_candidates(
    candidate_profiles: list[CandidateProfile],
    job_specification: JobSpecification,
) -> list[GapAnalysisResult]:
    """
    Analyze gaps for multiple candidates against same job.

    Args:
        candidate_profiles: List of candidate profiles
        job_specification: Job specification

    Returns:
        List of gap analysis results, sorted by overall fit (highest first)
    """
    results = []
    for profile in candidate_profiles:
        result = analyze_gaps(profile, job_specification)
        results.append(result)

    # Sort by overall fit score (descending)
    return sorted(results, key=lambda r: r.overall_fit_score, reverse=True)
