"""
Example integration of the preinterview pipeline components.

This script demonstrates how to use all components together:
1. Parse a resume
2. Enrich the profile with LinkedIn/GitHub data
3. Perform gap analysis
4. Generate an interview plan
"""
from __future__ import annotations

import asyncio

from .gap_analysis import analyze_gaps
from .interview_plan import InterviewPlanGenerator
from .models import (
    CandidateProfile,
    JobRequirement,
    JobSpecification,
    Skill,
    SkillLevel,
)


async def example_integration():
    """Run a complete example of the preinterview pipeline."""

    print("=" * 80)
    print("PREINTERVIEW PIPELINE INTEGRATION EXAMPLE")
    print("=" * 80)

    # Step 1: Create a sample candidate profile
    print("\n1. CANDIDATE PROFILE")
    print("-" * 40)

    candidate = CandidateProfile(
        candidate_id="C001",
        full_name="Alice Johnson",
        email="alice@example.com",
        phone="+1-555-123-4567",
        location="San Francisco, CA",
        current_title="Senior Software Engineer",
        total_experience_years=8.0,
        skills=[
            Skill(name="Python", level=SkillLevel.EXPERT),
            Skill(name="System Design", level=SkillLevel.ADVANCED),
            Skill(name="Java", level=SkillLevel.INTERMEDIATE),
            Skill(name="SQL", level=SkillLevel.ADVANCED),
        ],
    )

    print(f"Name: {candidate.full_name}")
    print(f"Title: {candidate.current_title}")
    print(f"Experience: {candidate.total_experience_years} years")
    print(f"Skills: {', '.join(s.name for s in candidate.skills)}")

    # Step 2: Create a job specification
    print("\n2. JOB SPECIFICATION")
    print("-" * 40)

    job = JobSpecification(
        job_id="J001",
        job_title="Senior Backend Engineer",
        job_description="We are seeking a senior backend engineer to lead our platform team.",
        min_experience_years=6.0,
        requirements=[
            JobRequirement(
                name="Python",
                level=SkillLevel.ADVANCED,
                importance=1.0,
            ),
            JobRequirement(
                name="System Design",
                level=SkillLevel.ADVANCED,
                importance=0.9,
            ),
            JobRequirement(
                name="Kubernetes",
                level=SkillLevel.INTERMEDIATE,
                importance=0.7,
            ),
            JobRequirement(
                name="Team Leadership",
                level=SkillLevel.INTERMEDIATE,
                importance=0.8,
            ),
        ],
    )

    print(f"Job Title: {job.job_title}")
    print(f"Requirements:")
    for req in job.requirements:
        print(f"  - {req.name}: {req.level.value}")

    # Step 3: Perform gap analysis
    print("\n3. GAP ANALYSIS")
    print("-" * 40)

    gap_result = analyze_gaps(
        candidate_profile=candidate,
        job_specification=job,
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
    )

    print(f"Overall Fit Score: {gap_result.overall_fit_score}%")
    print(f"Readiness Level: {gap_result.readiness_level}")

    if gap_result.critical_gaps:
        print(f"\nCritical Gaps ({len(gap_result.critical_gaps)}):")
        for gap in gap_result.critical_gaps:
            print(f"  - {gap.skill_name}: {gap.gap_severity}")

    if gap_result.significant_gaps:
        print(f"\nSignificant Gaps ({len(gap_result.significant_gaps)}):")
        for gap in gap_result.significant_gaps:
            print(f"  - {gap.skill_name}: {gap.gap_severity}")

    if gap_result.strengths:
        print(f"\nStrengths ({len(gap_result.strengths)}):")
        for strength in gap_result.strengths:
            print(f"  + {strength}")

    print(f"\nSummary: {gap_result.summary}")

    # Step 4: Generate interview plan
    print("\n4. INTERVIEW PLAN")
    print("-" * 40)

    generator = InterviewPlanGenerator()
    interview_plan = generator.generate_plan(
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        gap_analysis=gap_result,
        interview_format="full_loop",
    )

    print(f"Plan ID: {interview_plan.plan_id}")
    print(f"Interview Format: Full Loop")
    print(f"Duration: {interview_plan.interview_duration_minutes} minutes")
    print(f"Focus: {interview_plan.interview_focus}")

    print(f"\nCompetency Focus:")
    for competency in interview_plan.competency_focus:
        print(f"  - {competency}")

    print(f"\nInterview Questions ({len(interview_plan.questions)}):")
    for question in interview_plan.questions[:3]:
        print(f"  {question.question_id}: {question.question_text[:50]}...")

    if interview_plan.critical_gap_exploration:
        print(f"\nCritical Gap Exploration:")
        print(f"  {interview_plan.critical_gap_exploration[:100]}...")

    if interview_plan.risk_indicators:
        print(f"\nRisk Indicators:")
        for risk in interview_plan.risk_indicators[:3]:
            print(f"  ⚠ {risk[:60]}...")

    print("\n" + "=" * 80)
    print("INTEGRATION EXAMPLE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(example_integration())
