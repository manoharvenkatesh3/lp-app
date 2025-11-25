"""Unit tests for gap analysis module."""
from __future__ import annotations

import pytest

from .gap_analysis import (
    analyze_gaps,
    calculate_skill_match,
    classify_gap_severity,
    find_candidate_skill,
    normalize_skill_name,
)
from .models import (
    CandidateProfile,
    JobRequirement,
    JobSpecification,
    Skill,
    SkillLevel,
)


class TestSkillNameNormalization:
    """Tests for skill name normalization."""

    def test_normalize_lowercase(self):
        """Test normalizing to lowercase."""
        assert normalize_skill_name("PYTHON") == "python"
        assert normalize_skill_name("Python") == "python"

    def test_normalize_whitespace(self):
        """Test normalizing whitespace."""
        assert normalize_skill_name("  Python  ") == "python"


class TestSkillFinding:
    """Tests for finding skills in candidate profile."""

    def test_find_existing_skill(self):
        """Test finding a skill that exists."""
        profile = CandidateProfile(
            full_name="John",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.ADVANCED),
            ],
        )
        skill = find_candidate_skill(profile, "Python")
        assert skill is not None
        assert skill.name == "Python"

    def test_find_skill_case_insensitive(self):
        """Test finding skill with case mismatch."""
        profile = CandidateProfile(
            full_name="John",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.ADVANCED),
            ],
        )
        skill = find_candidate_skill(profile, "python")
        assert skill is not None

    def test_skill_not_found(self):
        """Test when skill doesn't exist."""
        profile = CandidateProfile(
            full_name="John",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.ADVANCED),
            ],
        )
        skill = find_candidate_skill(profile, "Java")
        assert skill is None


class TestSkillMatching:
    """Tests for skill matching."""

    def test_match_same_level(self):
        """Test matching skills at same level."""
        score = calculate_skill_match(SkillLevel.INTERMEDIATE, SkillLevel.INTERMEDIATE)
        assert score == 1.0

    def test_match_higher_level(self):
        """Test matching with higher candidate level."""
        score = calculate_skill_match(SkillLevel.EXPERT, SkillLevel.INTERMEDIATE)
        assert score == 1.0

    def test_match_lower_level(self):
        """Test matching with lower candidate level."""
        score = calculate_skill_match(SkillLevel.BEGINNER, SkillLevel.INTERMEDIATE)
        assert 0 < score < 1

    def test_match_missing_skill(self):
        """Test matching when skill is missing."""
        score = calculate_skill_match(None, SkillLevel.INTERMEDIATE)
        assert score == 0.0


class TestGapSeverityClassification:
    """Tests for gap severity classification."""

    def test_classify_none(self):
        """Test classifying no gap."""
        severity = classify_gap_severity(1.0)
        assert severity == "none"

    def test_classify_minor(self):
        """Test classifying minor gap."""
        severity = classify_gap_severity(0.85)
        assert severity == "minor"

    def test_classify_significant(self):
        """Test classifying significant gap."""
        severity = classify_gap_severity(0.65)
        assert severity == "significant"

    def test_classify_critical(self):
        """Test classifying critical gap."""
        severity = classify_gap_severity(0.1)
        assert severity == "critical"


class TestGapAnalysis:
    """Tests for gap analysis."""

    def test_analyze_perfect_match(self):
        """Test analysis with perfect match."""
        profile = CandidateProfile(
            candidate_id="C001",
            full_name="John",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.EXPERT),
            ],
        )
        job = JobSpecification(
            job_id="J001",
            job_title="Senior Engineer",
            job_description="Need expert Python developer",
            requirements=[
                JobRequirement(name="Python", level=SkillLevel.EXPERT),
            ],
        )
        result = analyze_gaps(profile, job)

        assert result.candidate_id == "C001"
        assert result.job_id == "J001"
        assert len(result.critical_gaps) == 0
        assert result.overall_fit_score == 100.0

    def test_analyze_with_gaps(self):
        """Test analysis with skill gaps."""
        profile = CandidateProfile(
            candidate_id="C001",
            full_name="John",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.INTERMEDIATE),
            ],
        )
        job = JobSpecification(
            job_id="J001",
            job_title="Senior Engineer",
            job_description="Need expert Python developer",
            requirements=[
                JobRequirement(name="Python", level=SkillLevel.EXPERT),
                JobRequirement(name="Kubernetes", level=SkillLevel.INTERMEDIATE),
            ],
        )
        result = analyze_gaps(profile, job)

        assert len(result.critical_gaps) > 0 or len(result.significant_gaps) > 0
        assert result.overall_fit_score < 100.0

    def test_analyze_missing_skills(self):
        """Test analysis with completely missing skills."""
        profile = CandidateProfile(
            candidate_id="C001",
            full_name="John",
            email="john@example.com",
            skills=[],
        )
        job = JobSpecification(
            job_id="J001",
            job_title="Senior Engineer",
            job_description="Need Python and Java developer",
            requirements=[
                JobRequirement(name="Python", level=SkillLevel.ADVANCED),
                JobRequirement(name="Java", level=SkillLevel.ADVANCED),
            ],
        )
        result = analyze_gaps(profile, job)

        assert len(result.critical_gaps) >= 2
        assert result.readiness_level == "not_suitable"

    def test_analyze_with_strengths(self):
        """Test analysis identifying strengths."""
        profile = CandidateProfile(
            candidate_id="C001",
            full_name="John",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.EXPERT),
                Skill(name="Machine Learning", level=SkillLevel.ADVANCED),
            ],
        )
        job = JobSpecification(
            job_id="J001",
            job_title="Senior Engineer",
            job_description="Need Python developer",
            requirements=[
                JobRequirement(name="Python", level=SkillLevel.INTERMEDIATE),
            ],
            nice_to_have_skills=["Machine Learning"],
        )
        result = analyze_gaps(profile, job)

        assert len(result.strengths) > 0

    def test_readiness_classification_ready(self):
        """Test readiness classification as ready."""
        profile = CandidateProfile(
            candidate_id="C001",
            full_name="John",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.EXPERT),
                Skill(name="Java", level=SkillLevel.ADVANCED),
            ],
        )
        job = JobSpecification(
            job_id="J001",
            job_title="Senior Engineer",
            job_description="Need Python and Java developer",
            requirements=[
                JobRequirement(name="Python", level=SkillLevel.ADVANCED),
                JobRequirement(name="Java", level=SkillLevel.INTERMEDIATE),
            ],
        )
        result = analyze_gaps(profile, job)

        assert result.readiness_level == "ready"
        assert result.overall_fit_score >= 85

    def test_readiness_classification_trainable(self):
        """Test readiness classification as trainable."""
        profile = CandidateProfile(
            candidate_id="C001",
            full_name="John",
            email="john@example.com",
            skills=[
                Skill(name="Python", level=SkillLevel.ADVANCED),
                Skill(name="Java", level=SkillLevel.BEGINNER),
            ],
        )
        job = JobSpecification(
            job_id="J001",
            job_title="Senior Engineer",
            job_description="Need Python and Java developer",
            requirements=[
                JobRequirement(name="Python", level=SkillLevel.ADVANCED),
                JobRequirement(name="Java", level=SkillLevel.INTERMEDIATE),
            ],
        )
        result = analyze_gaps(profile, job)

        assert result.readiness_level in ("trainable", "consider")
        assert 60 < result.overall_fit_score < 100
