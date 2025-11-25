"""Pytest configuration and fixtures."""
from __future__ import annotations

import pytest

from .models import (
    CandidateProfile,
    Education,
    JobRequirement,
    JobSpecification,
    ProfessionalExperience,
    Skill,
    SkillLevel,
)


@pytest.fixture
def sample_candidate():
    """Create a sample candidate profile for testing."""
    return CandidateProfile(
        candidate_id="C001",
        full_name="John Smith",
        email="john.smith@example.com",
        phone="+1-555-123-4567",
        location="San Francisco, CA",
        current_title="Senior Software Engineer",
        total_experience_years=7.0,
        experiences=[
            ProfessionalExperience(
                title="Senior Software Engineer",
                company="TechCorp",
                start_date="2021-01",
                description="Led team of 3 engineers",
            ),
            ProfessionalExperience(
                title="Software Engineer",
                company="StartupXYZ",
                start_date="2018-06",
                end_date="2020-12",
                duration_months=30,
                description="Full-stack development",
            ),
        ],
        skills=[
            Skill(name="Python", level=SkillLevel.EXPERT),
            Skill(name="Java", level=SkillLevel.ADVANCED),
            Skill(name="System Design", level=SkillLevel.ADVANCED),
            Skill(name="Leadership", level=SkillLevel.INTERMEDIATE),
        ],
        education=[
            Education(
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                institution="UC Berkeley",
                graduation_date="2017",
            ),
        ],
    )


@pytest.fixture
def sample_job_specification():
    """Create a sample job specification for testing."""
    return JobSpecification(
        job_id="J001",
        job_title="Senior Software Engineer",
        job_description="We are looking for an experienced senior software engineer to lead our backend team.",
        min_experience_years=5.0,
        preferred_skills=["Python", "System Design"],
        nice_to_have_skills=["Kubernetes", "AWS"],
        requirements=[
            JobRequirement(
                name="Python",
                category="technical",
                level=SkillLevel.ADVANCED,
                importance=1.0,
                nice_to_have=False,
            ),
            JobRequirement(
                name="System Design",
                category="technical",
                level=SkillLevel.ADVANCED,
                importance=0.9,
                nice_to_have=False,
            ),
            JobRequirement(
                name="Leadership",
                category="soft",
                level=SkillLevel.INTERMEDIATE,
                importance=0.7,
                nice_to_have=False,
            ),
            JobRequirement(
                name="Kubernetes",
                category="technical",
                level=SkillLevel.INTERMEDIATE,
                importance=0.5,
                nice_to_have=True,
            ),
        ],
    )


@pytest.fixture
def sample_underqualified_candidate():
    """Create a candidate with gaps for testing."""
    return CandidateProfile(
        candidate_id="C002",
        full_name="Jane Doe",
        email="jane.doe@example.com",
        location="New York, NY",
        current_title="Software Developer",
        total_experience_years=2.0,
        skills=[
            Skill(name="Python", level=SkillLevel.INTERMEDIATE),
            Skill(name="JavaScript", level=SkillLevel.INTERMEDIATE),
        ],
        education=[
            Education(
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                institution="State University",
                graduation_date="2022",
            ),
        ],
    )


@pytest.fixture
def sample_overqualified_candidate():
    """Create a candidate with strengths for testing."""
    return CandidateProfile(
        candidate_id="C003",
        full_name="Bob Johnson",
        email="bob.johnson@example.com",
        location="Seattle, WA",
        current_title="Principal Engineer",
        total_experience_years=12.0,
        skills=[
            Skill(name="Python", level=SkillLevel.EXPERT),
            Skill(name="Java", level=SkillLevel.EXPERT),
            Skill(name="System Design", level=SkillLevel.EXPERT),
            Skill(name="Leadership", level=SkillLevel.EXPERT),
            Skill(name="Kubernetes", level=SkillLevel.ADVANCED),
            Skill(name="AWS", level=SkillLevel.ADVANCED),
        ],
        education=[
            Education(
                degree="Master of Science",
                field_of_study="Computer Science",
                institution="Stanford",
                graduation_date="2015",
            ),
        ],
    )


@pytest.fixture
def resume_pdf_content():
    """Create mock PDF content for testing."""
    # Minimal PDF-like structure for testing
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font >> >> >> /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 100 >>
stream
BT
/F1 12 Tf
100 700 Td
(John Doe) Tj
100 650 Td
(john@example.com) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000229 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
328
%%EOF
"""


@pytest.fixture
def resume_docx_content():
    """Create minimal DOCX content for testing."""
    # This is a very simplified DOCX (ZIP) structure
    import io
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        # Minimal document.xml
        zf.writestr(
            "word/document.xml",
            b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>John Doe</w:t></w:r></w:p>
    <w:p><w:r><w:t>john@example.com</w:t></w:r></w:p>
  </w:body>
</w:document>
""",
        )
        # Minimal [Content_Types].xml
        zf.writestr(
            "[Content_Types].xml",
            b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
</Types>
""",
        )

    return buffer.getvalue()
