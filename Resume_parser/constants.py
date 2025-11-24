"""Core constants and seed data for the Eureka - AI Talent Discovery Engine."""
from __future__ import annotations

import textwrap
from typing import Dict, List

import pandas as pd

PRIMARY_COLOR = "#007BFF"
ACCENT_COLOR = "#10B981"
BACKGROUND_LIGHT = "#F9FAFB"
SURFACE_COLOR = "#FFFFFF"

REQUIRED_FIELDS = {
    "full_name": "Full Name",
    "email": "Email",
    "experience_years": "Years of Experience",
    "skills": "Key Skills",
    "current_role": "Current Role",
    "location": "Location",
}

DEFAULT_COLUMN_MAPPING = {
    "full_name": "full_name",
    "email": "email",
    "experience_years": "experience_years",
    "skills": "skills",
    "current_role": "current_role",
    "location": "location",
}

WORK_MODELS = ["Remote", "Hybrid", "Onsite"]

SAMPLE_JOB_DESCRIPTION = textwrap.dedent(
    """
    Eureka is seeking a Senior AI Recruiter to build and optimize talent pipelines for enterprise AI teams. The role requires
    hands-on sourcing, strong stakeholder management, and the ability to translate technical requirements into precise
    search strategies. Experience with large-model organizations, prompt engineering talent, and data-centric recruiting motions
    is highly valued. Candidates should be comfortable operating in hybrid environments with a high-velocity experimentation
    culture and communicate insights back to leadership quickly.
    """
).strip()

DEFAULT_WEIGHTS = {
    "skills_alignment": 50,
    "experience_fit": 30,
    "culture_impact": 20,
}

DEFAULT_SCREEN_CONFIG = {
    "job_title": "Senior AI Recruiter",
    "job_description": SAMPLE_JOB_DESCRIPTION,
    "preferred_work_model": "Hybrid",
    "minimum_experience": 5,
    "weights": DEFAULT_WEIGHTS.copy(),
}

DEFAULT_CANDIDATES: List[Dict[str, object]] = [
    {
        "id": "EKA-001",
        "full_name": "Amira Lopez",
        "email": "amira.lopez@talentlab.ai",
        "current_role": "Lead Talent Partner - Applied AI",
        "location": "New York, USA",
        "work_model": "Hybrid",
        "availability": "Immediate",
        "experience_years": 9.0,
        "skills": ["Python", "NLP", "Stakeholder Management", "ATS Automation", "Diversity Hiring"],
        "core_strengths": ["Exec stakeholder comms", "AI community events"],
        "recent_company": "Nova Robotics",
        "linkedin": "https://www.linkedin.com/in/amira-lopez",
        "culture_notes": "Mentors junior sourcers and drives inclusive interview panels.",
        "summary": "Scaled AI recruiting pods across US + Europe with a 92% offer acceptance rate.",
        "match_score": 88,
        "recommendation": "Strong",
    },
    {
        "id": "EKA-002",
        "full_name": "Hiro Tan",
        "email": "hiro.tan@vectorhire.io",
        "current_role": "Senior Technical Sourcer",
        "location": "Singapore",
        "work_model": "Remote",
        "availability": "30 days",
        "experience_years": 7.0,
        "skills": ["Computer Vision", "Boolean Search", "Talent Intelligence", "SQL", "Market Mapping"],
        "core_strengths": ["APAC expansion", "Process automation"],
        "recent_company": "Quantify Labs",
        "linkedin": "https://www.linkedin.com/in/hiro-tan",
        "culture_notes": "Drives async recruiting rituals and documents every sprint.",
        "summary": "Built zero-to-one ML talent pipelines, reducing time-to-fill by 35%.",
        "match_score": 82,
        "recommendation": "Strong",
    },
    {
        "id": "EKA-003",
        "full_name": "Selene Mendez",
        "email": "selene.mendez@uplink.io",
        "current_role": "People Scientist",
        "location": "Austin, USA",
        "work_model": "Hybrid",
        "availability": "Immediate",
        "experience_years": 6.0,
        "skills": ["Behavioral Interviewing", "Analytics", "Storytelling", "Program Design"],
        "core_strengths": ["Culture diagnostics", "Enablement"],
        "recent_company": "Horizon Cloud",
        "linkedin": "https://www.linkedin.com/in/selene-mendez",
        "culture_notes": "Champions narrative scorecards and amplifies employee stories.",
        "summary": "Operationalized AI talent roadmaps with leadership workshops across 5 countries.",
        "match_score": 76,
        "recommendation": "Balanced",
    },
    {
        "id": "EKA-004",
        "full_name": "Gabriel Singh",
        "email": "gabriel.singh@originrecruit.com",
        "current_role": "Principal Recruiter - GenAI",
        "location": "Toronto, Canada",
        "work_model": "Hybrid",
        "availability": "60 days",
        "experience_years": 11.0,
        "skills": ["Staffing Leadership", "RAG", "Offer Negotiations", "Employer Branding"],
        "core_strengths": ["Executive calibration", "Tier-1 vendor ops"],
        "recent_company": "Helix BioWorks",
        "linkedin": "https://www.linkedin.com/in/gabriel-singh",
        "culture_notes": "Facilitates post-offer retros to tighten feedback loops.",
        "summary": "Closed 40+ Staff level AI roles in 2023 while leading a 6-person pod.",
        "match_score": 91,
        "recommendation": "Strong",
    },
    {
        "id": "EKA-005",
        "full_name": "Priya Menon",
        "email": "priya.menon@arcbridge.ai",
        "current_role": "Technical Recruiter",
        "location": "Bengaluru, India",
        "work_model": "Onsite",
        "availability": "Immediate",
        "experience_years": 5.0,
        "skills": ["Embedded AI", "ATS Workflows", "Hiring Analytics", "University Programs"],
        "core_strengths": ["Programmatic outreach", "Vendor partnerships"],
        "recent_company": "ArcBridge AI",
        "linkedin": "https://www.linkedin.com/in/priya-menon",
        "culture_notes": "Loves building transparent hiring dashboards for business partners.",
        "summary": "Established a pan-India AI fellowship pipeline feeding 15 hires per quarter.",
        "match_score": 73,
        "recommendation": "Balanced",
    },
    {
        "id": "EKA-006",
        "full_name": "Noah Peters",
        "email": "noah.peters@fluidtalent.co",
        "current_role": "Recruiting Operations Lead",
        "location": "London, UK",
        "work_model": "Hybrid",
        "availability": "45 days",
        "experience_years": 8.0,
        "skills": ["Process Design", "Talent Analytics", "Change Management", "Automation"],
        "core_strengths": ["Systems thinking", "Global mobility"],
        "recent_company": "Fluid Talent",
        "linkedin": "https://www.linkedin.com/in/noah-peters",
        "culture_notes": "Introduced retros, betas, and runbooks for recruiting squads.",
        "summary": "Launched a recruiting ops hub that accelerates experimentation by 60%.",
        "match_score": 69,
        "recommendation": "Watch",
    },
    {
        "id": "EKA-007",
        "full_name": "Larissa Chen",
        "email": "larissa.chen@signalhire.net",
        "current_role": "Senior Sourcer - Applied Science",
        "location": "San Francisco, USA",
        "work_model": "Remote",
        "availability": "Immediate",
        "experience_years": 8.5,
        "skills": ["Applied Science", "Prompt Engineering", "Outreach Sequencing", "Community Building"],
        "core_strengths": ["Diverse pipelines", "Brand partnerships"],
        "recent_company": "SignalHire",
        "linkedin": "https://www.linkedin.com/in/larissa-chen",
        "culture_notes": "Hosts AI talent salons and speaks at industry panels.",
        "summary": "Designed AI/ML prospect experiences that doubled warm reply rates.",
        "match_score": 87,
        "recommendation": "Strong",
    },
    {
        "id": "EKA-008",
        "full_name": "Mateo Ruiz",
        "email": "mateo.ruiz@helixpeople.io",
        "current_role": "Recruiting Analyst",
        "location": "Mexico City, MX",
        "work_model": "Remote",
        "availability": "15 days",
        "experience_years": 4.0,
        "skills": ["Market Intelligence", "Candidate Research", "Power BI", "Scripting"],
        "core_strengths": ["Insight reporting", "Pipeline QA"],
        "recent_company": "Helix People",
        "linkedin": "https://www.linkedin.com/in/mateo-ruiz",
        "culture_notes": "Runs cross-team analytics guild and documents learnings weekly.",
        "summary": "Builds precise market scans for new AI hubs across LATAM.",
        "match_score": 65,
        "recommendation": "Watch",
    },
]

RECOMMENDATION_COLORS = {
    "Strong": ACCENT_COLOR,
    "Balanced": "#F97316",
    "Watch": "#F43F5E",
}

MAX_TOP_CANDIDATES = 7


def load_default_candidates() -> pd.DataFrame:
    """Return a DataFrame copy of the seed candidate dataset."""
    df = pd.DataFrame(DEFAULT_CANDIDATES)
    return df.copy()
