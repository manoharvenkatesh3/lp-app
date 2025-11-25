"""Resume parsing module for PDF/DOCX extraction and normalization."""
from __future__ import annotations

import hashlib
import io
import re
from typing import Optional, Tuple

from docx import Document
from pdfminer.high_level import extract_text

from .models import CandidateProfile, Education, ProfessionalExperience, Skill, SkillLevel


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content."""
    try:
        pdf_file = io.BytesIO(file_content)
        text = extract_text(pdf_file)
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file content."""
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {str(e)}")


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text."""
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    phone_pattern = r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?(\d{3}[-.\s]?)(\d{4})"
    matches = re.findall(phone_pattern, text)
    return matches[0][0] + matches[0][1] if matches else None


def extract_name(text: str) -> Optional[str]:
    """Extract name from resume (usually first line or near top)."""
    lines = text.split("\n")
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line and len(line) < 100 and not any(
            keyword in line.lower()
            for keyword in ["phone", "email", "address", "linkedin", "github"]
        ):
            return line
    return None


def extract_location(text: str) -> Optional[str]:
    """Extract location from resume text."""
    # Look for patterns like "City, State/Country" or "City, Country"
    location_pattern = r"(?:Location|Based in|Located in|From):?\s*([^\n]+?)(?:\n|$)"
    match = re.search(location_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_experiences(text: str) -> list[ProfessionalExperience]:
    """Extract work experience entries from resume text."""
    experiences: list[ProfessionalExperience] = []

    # Look for experience sections
    exp_section_pattern = (
        r"(?:work\s+experience|professional\s+experience|employment|experience)(.*?)(?="
        r"education|skills|projects|certification|$)"
    )
    match = re.search(exp_section_pattern, text, re.IGNORECASE | re.DOTALL)

    if not match:
        return experiences

    exp_text = match.group(1)

    # Parse individual job entries - look for job title followed by company
    # This is a simplified extraction
    job_pattern = r"([^\n]+?)\s+[|•-]\s+([^\n]+?)(?:\n|$)"
    job_matches = re.finditer(job_pattern, exp_text)

    for job_match in job_matches:
        title = job_match.group(1).strip()
        company = job_match.group(2).strip()

        if title and company and len(title) < 100 and len(company) < 100:
            experiences.append(
                ProfessionalExperience(
                    title=title,
                    company=company,
                    description=None,
                )
            )

    return experiences


def extract_skills(text: str) -> list[Skill]:
    """Extract skills from resume text."""
    skills: list[Skill] = []

    # Look for skills section
    skills_section_pattern = r"(?:skills|technical\s+skills|competencies)(.*?)(?=education|experience|project|$)"
    match = re.search(skills_section_pattern, text, re.IGNORECASE | re.DOTALL)

    if not match:
        return skills

    skills_text = match.group(1)

    # Split by common separators
    skill_list = re.split(r"[,;•\n]", skills_text)

    # Clean and create skill objects
    for skill_str in skill_list:
        skill_str = skill_str.strip()
        if skill_str and len(skill_str) < 100:
            # Remove common prefixes/suffixes
            skill_name = re.sub(r"^\d+\.\s*", "", skill_str)
            skill_name = skill_name.strip()
            if skill_name:
                skills.append(
                    Skill(
                        name=skill_name,
                        level=SkillLevel.INTERMEDIATE,
                    )
                )

    return skills


def extract_education(text: str) -> list[Education]:
    """Extract education entries from resume text."""
    education: list[Education] = []

    # Look for education section
    edu_section_pattern = r"(?:education|academic\s+background|degree)(.*?)(?=skills|experience|project|$)"
    match = re.search(edu_section_pattern, text, re.IGNORECASE | re.DOTALL)

    if not match:
        return education

    edu_text = match.group(1)

    # Look for degree patterns (Bachelor's, Master's, PhD, etc.)
    degree_pattern = r"(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.)[^\n]*in\s+([^\n,]+)"
    degree_matches = re.finditer(degree_pattern, edu_text, re.IGNORECASE)

    for degree_match in degree_matches:
        degree_type = degree_match.group(1)
        field = degree_match.group(2).strip()

        education.append(
            Education(
                degree=degree_type,
                field_of_study=field,
                institution="Unknown",
            )
        )

    return education


def calculate_experience_years(text: str) -> float:
    """Estimate total years of experience from resume text."""
    # Look for "X years" or "X+ years" patterns
    years_pattern = r"(\d+)\+?\s*years\s+of\s+experience"
    matches = re.findall(years_pattern, text, re.IGNORECASE)

    if matches:
        # Return the first (likely most recent/total) number
        return float(matches[0])

    # Fallback: count the number of experience entries
    exp_count = text.lower().count("years")
    return float(exp_count) if exp_count > 0 else 0.0


def compute_file_hash(file_content: bytes) -> str:
    """Compute SHA256 hash of file for deduplication."""
    return hashlib.sha256(file_content).hexdigest()


def parse_resume(
    file_content: bytes,
    file_extension: str,
    candidate_name: Optional[str] = None,
    candidate_email: Optional[str] = None,
) -> Tuple[CandidateProfile, float, list[str]]:
    """
    Parse resume file and return normalized CandidateProfile.

    Args:
        file_content: Raw file bytes
        file_extension: File extension ('pdf' or 'docx')
        candidate_name: Optional pre-filled candidate name
        candidate_email: Optional pre-filled candidate email

    Returns:
        Tuple of (CandidateProfile, parsing_confidence, parsing_warnings)
    """
    warnings: list[str] = []
    confidence = 1.0

    # Extract text based on file type
    if file_extension.lower() in ("pdf", ".pdf"):
        raw_text = extract_text_from_pdf(file_content)
    elif file_extension.lower() in ("docx", ".docx", "doc", ".doc"):
        raw_text = extract_text_from_docx(file_content)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    if not raw_text or len(raw_text.strip()) < 50:
        raise ValueError("Resume text is too short or empty")

    # Extract fields
    name = candidate_name or extract_name(raw_text)
    email = candidate_email or extract_email(raw_text)
    phone = extract_phone(raw_text)
    location = extract_location(raw_text)
    experiences = extract_experiences(raw_text)
    skills = extract_skills(raw_text)
    education = extract_education(raw_text)
    experience_years = calculate_experience_years(raw_text)

    # Set confidence based on what we could extract
    if not email:
        confidence -= 0.1
        warnings.append("Could not extract email address")
    if not name:
        confidence -= 0.1
        warnings.append("Could not extract candidate name")
    if not skills:
        confidence -= 0.05
        warnings.append("Could not extract skills section")

    # Create profile
    current_title = experiences[0].title if experiences else None

    profile = CandidateProfile(
        full_name=name or "Unknown",
        email=email or "unknown@example.com",
        phone=phone,
        location=location,
        current_title=current_title,
        total_experience_years=experience_years,
        experiences=experiences,
        skills=skills,
        education=education,
        raw_cv_content=raw_text,
        cv_file_hash=compute_file_hash(file_content),
    )

    return profile, max(confidence, 0.0), warnings
