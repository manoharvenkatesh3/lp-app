"""Utility helpers for data ingestion, scoring, and presentation."""
from __future__ import annotations

import io
import json
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import httpx
import pandas as pd

from .constants import (
    DEFAULT_COLUMN_MAPPING,
    MAX_TOP_CANDIDATES,
    RECOMMENDATION_COLORS,
    REQUIRED_FIELDS,
)

STOP_WORDS = {
    "and",
    "the",
    "with",
    "for",
    "to",
    "of",
    "in",
    "a",
    "an",
    "is",
    "on",
    "as",
    "be",
    "by",
    "at",
}


def normalize_skill_value(value: object) -> List[str]:
    """Convert different formats into a clean list of skills/keywords."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, (set, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        separators = r"[\n\r,;•|/]"
        tokens = [token.strip() for token in re.split(separators, value) if token.strip()]
        return tokens
    if pd.isna(value):  # type: ignore[arg-type]
        return []
    return [str(value).strip()]


def parse_uploaded_file(uploaded_file) -> pd.DataFrame:
    """Parse CSV, Excel, or JSON files uploaded locally."""
    if uploaded_file is None:
        raise ValueError("No file supplied.")

    file_name = uploaded_file.name.lower()
    uploaded_file.seek(0)

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if file_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    if file_name.endswith(".json"):
        data = json.load(uploaded_file)
        if isinstance(data, dict):
            data = data.get("candidates") or data.get("rows") or data
        if isinstance(data, list):
            return pd.DataFrame(data)
        raise ValueError("JSON structure must be a list of candidate objects.")
    raise ValueError("Supported formats: CSV, XLSX, XLS, JSON.")


def extract_sheet_identifiers(value: str) -> Tuple[Optional[str], Optional[str]]:
    if not value:
        return None, None
    value = value.strip()
    gid_match = re.search(r"gid=(\d+)", value)
    gid = gid_match.group(1) if gid_match else None
    if "docs.google.com" in value:
        match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", value)
        sheet_id = match.group(1) if match else None
        return sheet_id, gid
    return value, gid


def fetch_google_sheet(sheet_value: str) -> pd.DataFrame:
    sheet_id, gid = extract_sheet_identifiers(sheet_value)
    if not sheet_id:
        raise ValueError("Please provide a valid Google Sheets URL or ID.")

    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid:
        csv_url += f"&gid={gid}"

    try:
        response = httpx.get(csv_url, timeout=20.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ValueError(f"Google Sheets returned status {exc.response.status_code}.") from exc
    except httpx.RequestError as exc:
        raise ConnectionError("Unable to reach Google Sheets. Check the URL or your connection.") from exc

    return pd.read_csv(io.StringIO(response.text))


def apply_column_mapping(df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> pd.DataFrame:
    """Rename or synthesize required Eureka columns via user-defined mapping."""
    mapping = mapping or DEFAULT_COLUMN_MAPPING
    normalized = pd.DataFrame()

    for target_key in REQUIRED_FIELDS.keys():
        candidate_column = mapping.get(target_key)
        if candidate_column and candidate_column in df.columns:
            normalized[target_key] = df[candidate_column]
        else:
            normalized[target_key] = None

    for col in df.columns:
        if col not in normalized.columns:
            normalized[col] = df[col]

    if "id" not in normalized.columns:
        normalized.insert(0, "id", [f"EKA-{idx:03d}" for idx in range(1, len(normalized) + 1)])

    normalized["experience_years"] = pd.to_numeric(
        normalized["experience_years"], errors="coerce"
    ).fillna(0.0)

    normalized["skills"] = normalized["skills"].apply(normalize_skill_value)

    if "work_model" not in normalized.columns:
        normalized["work_model"] = "Hybrid"

    if "availability" not in normalized.columns:
        normalized["availability"] = "30 days"

    normalized["match_score"] = pd.to_numeric(
        normalized.get("match_score", 0), errors="coerce"
    ).fillna(0)

    if "recommendation" not in normalized.columns:
        normalized["recommendation"] = "Pending"

    normalized["full_name"] = normalized["full_name"].fillna("Unknown Candidate")
    normalized["current_role"] = normalized["current_role"].fillna("—")
    normalized["location"] = normalized["location"].fillna("—")

    return normalized


def compute_summary_metrics(df: pd.DataFrame) -> Dict[str, object]:
    if df is None or df.empty:
        return {
            "total": 0,
            "average_experience": 0.0,
            "immediate_ready": 0,
            "remote_ready": 0,
        }

    immediate_ready = df["availability"].fillna("").str.contains("immediate", case=False, na=False).sum()
    remote_ready = df["work_model"].fillna("").str.contains("remote", case=False, na=False).sum()

    return {
        "total": int(len(df)),
        "average_experience": round(df["experience_years"].mean(), 1),
        "immediate_ready": int(immediate_ready),
        "remote_ready": int(remote_ready),
    }


def extract_job_keywords(job_title: str, job_description: str) -> List[str]:
    combined = f"{job_title or ''} {job_description or ''}".lower()
    tokens = re.findall(r"[a-z0-9+#]{3,}", combined)
    keywords = sorted({token for token in tokens if token not in STOP_WORDS})
    return keywords


def _skill_alignment(candidate_skills: List[str], keywords: Sequence[str]) -> float:
    if not keywords:
        return 0.7
    skills = {skill.lower() for skill in candidate_skills}
    matched = len(skills.intersection(set(keywords)))
    return min(1.0, matched / max(1, len(keywords) * 0.5))


def _experience_fit(experience: float, minimum: int) -> float:
    if minimum <= 0:
        return 1.0
    ratio = experience / float(minimum)
    if ratio >= 1:
        return 1.0
    return max(0.2, ratio)


def _culture_fit(work_model: str, preferred: str) -> float:
    work_model = (work_model or "Hybrid").strip().title()
    preferred = (preferred or "Hybrid").strip().title()
    if work_model == preferred:
        return 1.0
    if preferred == "Hybrid":
        return 0.85
    if work_model == "Hybrid":
        return 0.9
    return 0.55


def classify_recommendation(score: float) -> str:
    if score >= 85:
        return "Strong"
    if score >= 70:
        return "Balanced"
    return "Watch"


def score_candidates(
    df: pd.DataFrame,
    *,
    job_title: str,
    job_description: str,
    weights: Dict[str, int],
    preferred_work_model: str,
    minimum_experience: int,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    keywords = extract_job_keywords(job_title, job_description)
    total_weight = sum(weights.values()) or 1
    normalized_weights = {key: value / total_weight for key, value in weights.items()}

    scored = df.copy()
    scored["skills_alignment_score"] = scored["skills"].apply(lambda skills: _skill_alignment(skills, keywords))
    scored["experience_fit_score"] = scored["experience_years"].apply(
        lambda val: _experience_fit(val, minimum_experience)
    )
    scored["culture_impact_score"] = scored["work_model"].apply(
        lambda val: _culture_fit(val, preferred_work_model)
    )

    scored["match_score"] = (
        scored["skills_alignment_score"] * normalized_weights.get("skills_alignment", 0)
        + scored["experience_fit_score"] * normalized_weights.get("experience_fit", 0)
        + scored["culture_impact_score"] * normalized_weights.get("culture_impact", 0)
    ) * 100

    scored["match_score"] = scored["match_score"].round(1)
    scored["recommendation"] = scored["match_score"].apply(classify_recommendation)

    return scored.sort_values("match_score", ascending=False).reset_index(drop=True)


def top_candidates(df: pd.DataFrame, limit: int = MAX_TOP_CANDIDATES) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    return df.nlargest(limit, "match_score").reset_index(drop=True)


def recommendation_color(label: str) -> str:
    return RECOMMENDATION_COLORS.get(label, "#6B7280")


def chunked(items: Sequence[Dict[str, object]], chunk_size: int) -> Iterable[List[Dict[str, object]]]:
    chunk: List[Dict[str, object]] = []
    for item in items:
        chunk.append(item)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
