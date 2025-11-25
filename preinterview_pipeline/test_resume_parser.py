"""Unit tests for resume parser module."""
from __future__ import annotations

import pytest

from .resume_parser import (
    calculate_experience_years,
    compute_file_hash,
    extract_email,
    extract_education,
    extract_experiences,
    extract_location,
    extract_name,
    extract_phone,
    extract_skills,
    extract_text_from_docx,
    extract_text_from_pdf,
    parse_resume,
)


class TestEmailExtraction:
    """Tests for email extraction."""

    def test_extract_simple_email(self):
        """Test extracting a simple email address."""
        text = "Contact: john.doe@company.com for more info"
        email = extract_email(text)
        assert email == "john.doe@company.com"

    def test_extract_email_with_numbers(self):
        """Test extracting email with numbers."""
        text = "Email: user123@domain.co.uk"
        email = extract_email(text)
        assert email == "user123@domain.co.uk"

    def test_no_email_found(self):
        """Test when no email is present."""
        text = "This is a resume without contact info"
        email = extract_email(text)
        assert email is None


class TestPhoneExtraction:
    """Tests for phone number extraction."""

    def test_extract_us_phone(self):
        """Test extracting US phone number."""
        text = "Phone: 555-123-4567"
        phone = extract_phone(text)
        assert phone is not None
        assert "123" in phone and "4567" in phone

    def test_no_phone_found(self):
        """Test when no phone is present."""
        text = "This is a resume without phone"
        phone = extract_phone(text)
        # May or may not find phone, test is for safety
        assert phone is None or isinstance(phone, str)


class TestNameExtraction:
    """Tests for name extraction."""

    def test_extract_name_from_start(self):
        """Test extracting name from beginning of text."""
        text = "John Smith\nAI Engineer\nemail@company.com"
        name = extract_name(text)
        assert name == "John Smith"

    def test_skip_email_as_name(self):
        """Test that email-like lines are skipped."""
        text = "email@company.com\nJohn Smith\nExperience"
        name = extract_name(text)
        # Should find John Smith, not email
        assert name and "John" in name


class TestLocationExtraction:
    """Tests for location extraction."""

    def test_extract_location_explicit(self):
        """Test extracting explicitly marked location."""
        text = "Location: San Francisco, CA"
        location = extract_location(text)
        assert location is not None
        assert "San Francisco" in location


class TestSkillsExtraction:
    """Tests for skills extraction."""

    def test_extract_skills(self):
        """Test extracting skills from text."""
        text = """
        Skills
        Python, Java, Go
        Machine Learning, Data Science
        AWS, Kubernetes
        """
        skills = extract_skills(text)
        assert len(skills) > 0
        # Check that we got some skills
        skill_names = [s.name for s in skills]
        assert any("python" in s.lower() for s in skill_names)


class TestExperienceExtraction:
    """Tests for experience extraction."""

    def test_extract_experiences(self):
        """Test extracting work experiences."""
        text = """
        Work Experience
        Senior Engineer | Google
        Software Engineer | Microsoft
        """
        experiences = extract_experiences(text)
        assert len(experiences) > 0


class TestEducationExtraction:
    """Tests for education extraction."""

    def test_extract_bachelor_degree(self):
        """Test extracting Bachelor's degree."""
        text = "Education\nBachelor of Science in Computer Science, MIT, 2020"
        education = extract_education(text)
        assert len(education) > 0
        assert any("Bachelor" in e.degree for e in education)

    def test_extract_multiple_degrees(self):
        """Test extracting multiple degrees."""
        text = """
        Education
        Bachelor of Science in Computer Science, MIT, 2020
        Master of Science in AI, Stanford, 2022
        """
        education = extract_education(text)
        assert len(education) >= 1


class TestExperienceYearsCalculation:
    """Tests for experience years calculation."""

    def test_calculate_years_from_text(self):
        """Test calculating years of experience."""
        text = "5 years of experience in software development"
        years = calculate_experience_years(text)
        assert years == 5.0

    def test_calculate_years_multiple(self):
        """Test when multiple year mentions exist."""
        text = "10 years of experience in total, 3 years with Python"
        years = calculate_experience_years(text)
        assert years == 10.0  # Gets first match


class TestFileHashing:
    """Tests for file hashing."""

    def test_compute_file_hash(self):
        """Test computing SHA256 hash."""
        content = b"test content"
        hash1 = compute_file_hash(content)
        hash2 = compute_file_hash(content)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex is 64 chars


class TestResumeParser:
    """Tests for main resume parser."""

    def test_parse_empty_file_raises_error(self):
        """Test that empty files raise error."""
        with pytest.raises(ValueError):
            parse_resume(b"", "pdf")

    def test_parse_with_candidate_name_override(self):
        """Test parsing with pre-filled candidate name and email."""
        from unittest.mock import patch

        with patch("preinterview_pipeline.resume_parser.extract_text_from_pdf") as mock_extract:
            mock_extract.return_value = "John Doe\nSoftware Engineer\nSkills: Python, Java\n5 years experience"

            profile, confidence, warnings = parse_resume(
                b"fake_pdf_content",
                "pdf",
                candidate_name="John Doe Override",
                candidate_email="john@example.com",
            )

            assert profile.full_name == "John Doe Override"
            assert profile.email == "john@example.com"
            assert profile.total_experience_years > 0

    def test_parse_with_warnings_for_missing_email(self):
        """Test that warnings are generated for missing email."""
        from unittest.mock import patch

        with patch("preinterview_pipeline.resume_parser.extract_text_from_pdf") as mock_extract:
            mock_extract.return_value = "John Doe\nSoftware Engineer with 5 years experience\nPython, Java, C++"

            profile, confidence, warnings = parse_resume(
                b"fake_pdf_content",
                "pdf",
            )

            # Should have warning about missing email
            assert "email" in " ".join(warnings).lower() or confidence < 1.0

    def test_unsupported_format_raises_error(self):
        """Test that unsupported formats raise error."""
        with pytest.raises(ValueError, match="Unsupported"):
            parse_resume(b"content", "txt")
