"""Unit tests for interview plan generation."""
from __future__ import annotations

import pytest

from .gap_analysis import analyze_gaps
from .interview_plan import InterviewPlanGenerator
from .models import (
    CandidateProfile,
    GapAnalysisResult,
    JobRequirement,
    JobSpecification,
    Skill,
    SkillLevel,
)


class TestInterviewPlanGenerator:
    """Tests for interview plan generation."""

    @pytest.fixture
    def generator(self):
        """Create an interview plan generator."""
        return InterviewPlanGenerator()

    @pytest.fixture
    def candidate_profile(self):
        """Create a sample candidate profile."""
        return CandidateProfile(
            candidate_id="C001",
            full_name="John Doe",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.ADVANCED),
                Skill(name="Java", level=SkillLevel.INTERMEDIATE),
            ],
        )

    @pytest.fixture
    def job_spec(self):
        """Create a sample job specification."""
        return JobSpecification(
            job_id="J001",
            job_title="Senior Software Engineer",
            job_description="Looking for an experienced engineer",
            requirements=[
                JobRequirement(name="Python", level=SkillLevel.ADVANCED),
                JobRequirement(name="System Design", level=SkillLevel.ADVANCED),
                JobRequirement(name="Leadership", level=SkillLevel.INTERMEDIATE),
            ],
        )

    def test_generate_phone_screen_plan(self, generator, candidate_profile, job_spec):
        """Test generating phone screen interview plan."""
        gap_analysis = analyze_gaps(candidate_profile, job_spec)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="phone_screen",
        )

        assert plan.plan_id is not None
        assert plan.candidate_id == "C001"
        assert plan.job_id == "J001"
        assert plan.interview_duration_minutes == 30
        assert len(plan.questions) > 0

    def test_generate_technical_plan(self, generator, candidate_profile, job_spec):
        """Test generating technical interview plan."""
        gap_analysis = analyze_gaps(candidate_profile, job_spec)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="technical",
        )

        assert plan.interview_duration_minutes == 60
        assert any("technical" in str(c).lower() for c in plan.competency_focus)

    def test_generate_full_loop_plan(self, generator, candidate_profile, job_spec):
        """Test generating full loop interview plan."""
        gap_analysis = analyze_gaps(candidate_profile, job_spec)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="full_loop",
        )

        assert plan.interview_duration_minutes == 180
        assert len(plan.questions) >= 4  # Multiple rounds

    def test_generate_executive_plan(self, generator, candidate_profile, job_spec):
        """Test generating executive interview plan."""
        gap_analysis = analyze_gaps(candidate_profile, job_spec)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="executive",
        )

        assert plan.interview_duration_minutes == 45
        assert any("leadership" in str(c).lower() for c in plan.competency_focus)

    def test_plan_has_questions_for_all_competencies(
        self, generator, candidate_profile, job_spec
    ):
        """Test that plan has questions for all selected competencies."""
        gap_analysis = analyze_gaps(candidate_profile, job_spec)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="full_loop",
        )

        # Each competency should have at least one question
        competencies_in_questions = set(q.competency for q in plan.questions)
        for comp in plan.competency_focus:
            assert comp in competencies_in_questions

    def test_plan_includes_critical_gap_guidance(self, generator, candidate_profile, job_spec):
        """Test that plan includes guidance for critical gaps."""
        gap_analysis = analyze_gaps(candidate_profile, job_spec)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="full_loop",
        )

        if gap_analysis.critical_gaps:
            assert plan.critical_gap_exploration is not None

    def test_plan_includes_strength_validation(self, generator, candidate_profile, job_spec):
        """Test that plan includes guidance for strength validation."""
        # Create a profile with matching skills
        profile = CandidateProfile(
            candidate_id="C001",
            full_name="John Doe",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.EXPERT),
                Skill(name="System Design", level=SkillLevel.ADVANCED),
            ],
        )
        job = JobSpecification(
            job_id="J001",
            job_title="Senior Engineer",
            job_description="Need expert",
            requirements=[
                JobRequirement(name="Python", level=SkillLevel.ADVANCED),
                JobRequirement(name="System Design", level=SkillLevel.ADVANCED),
            ],
        )

        gap_analysis = analyze_gaps(profile, job)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="full_loop",
        )

        # Should have strength validation guidance
        assert plan.strength_validation is not None or not gap_analysis.strengths

    def test_plan_includes_risk_indicators(self, generator, candidate_profile, job_spec):
        """Test that plan includes risk indicators."""
        gap_analysis = analyze_gaps(candidate_profile, job_spec)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="full_loop",
        )

        assert len(plan.risk_indicators) > 0

    def test_plan_questions_have_follow_ups(self, generator, candidate_profile, job_spec):
        """Test that questions include follow-up prompts."""
        gap_analysis = analyze_gaps(candidate_profile, job_spec)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="full_loop",
        )

        # Most questions should have follow-ups
        questions_with_followups = sum(1 for q in plan.questions if q.follow_ups)
        assert questions_with_followups > 0

    def test_plan_questions_have_evaluation_criteria(
        self, generator, candidate_profile, job_spec
    ):
        """Test that questions include evaluation criteria."""
        gap_analysis = analyze_gaps(candidate_profile, job_spec)

        plan = generator.generate_plan(
            candidate_id="C001",
            job_id="J001",
            gap_analysis=gap_analysis,
            interview_format="full_loop",
        )

        # All questions should have evaluation criteria
        assert all(q.evaluation_criteria for q in plan.questions)
