"""Bias detection and filtering middleware."""
from __future__ import annotations

import re
from typing import Any

# Bias indicators to flag
BIAS_KEYWORDS = {
    "age": ["young", "old", "mature", "energetic", "recent graduate"],
    "gender": ["he", "she", "guy", "girl", "man", "woman", "female", "male"],
    "race": ["diversity", "culture fit", "native", "foreign"],
    "disability": ["healthy", "able-bodied", "normal"],
    "appearance": ["attractive", "professional appearance", "well-groomed"],
    "family": ["single", "married", "children", "family status"],
}

# Approved inclusive language alternatives
INCLUSIVE_ALTERNATIVES = {
    "young": "early-career",
    "old": "experienced",
    "mature": "seasoned",
    "guy": "person",
    "girl": "person",
    "culture fit": "team alignment",
    "native": "fluent in",
}


def check_for_bias(text: str) -> dict[str, Any]:
    """
    Check text for potential bias indicators.
    
    Returns a dictionary with:
    - passed: bool indicating if text passes bias check
    - flags: list of detected bias indicators
    - suggestions: list of inclusive alternatives
    """
    if not text:
        return {"passed": True, "flags": [], "suggestions": []}
    
    text_lower = text.lower()
    flags = []
    suggestions = []
    
    for category, keywords in BIAS_KEYWORDS.items():
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                flags.append({
                    "category": category,
                    "keyword": keyword,
                    "context": _extract_context(text, keyword),
                })
                
                if keyword in INCLUSIVE_ALTERNATIVES:
                    suggestions.append({
                        "original": keyword,
                        "alternative": INCLUSIVE_ALTERNATIVES[keyword],
                    })
    
    return {
        "passed": len(flags) == 0,
        "flags": flags,
        "suggestions": suggestions,
        "severity": "high" if len(flags) > 3 else "medium" if len(flags) > 0 else "low",
    }


def _extract_context(text: str, keyword: str, context_length: int = 50) -> str:
    """Extract context around a keyword in text."""
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    idx = text_lower.find(keyword_lower)
    if idx == -1:
        return ""
    
    start = max(0, idx - context_length)
    end = min(len(text), idx + len(keyword) + context_length)
    
    context = text[start:end]
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."
    
    return context


def sanitize_feedback(feedback: str) -> str:
    """
    Sanitize feedback text by replacing biased terms with inclusive alternatives.
    """
    sanitized = feedback
    
    for original, alternative in INCLUSIVE_ALTERNATIVES.items():
        pattern = r'\b' + re.escape(original) + r'\b'
        sanitized = re.sub(pattern, alternative, sanitized, flags=re.IGNORECASE)
    
    return sanitized


def validate_scorecard(scorecard_data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate scorecard data for bias.
    
    Returns validation result with bias check details.
    """
    bias_results = []
    
    # Check feedback text
    if "detailed_feedback" in scorecard_data:
        feedback_check = check_for_bias(scorecard_data["detailed_feedback"])
        if not feedback_check["passed"]:
            bias_results.append({
                "field": "detailed_feedback",
                "result": feedback_check,
            })
    
    # Check strengths
    if "strengths" in scorecard_data:
        for strength in scorecard_data.get("strengths", []):
            if isinstance(strength, str):
                strength_check = check_for_bias(strength)
                if not strength_check["passed"]:
                    bias_results.append({
                        "field": "strengths",
                        "result": strength_check,
                    })
    
    # Check weaknesses
    if "weaknesses" in scorecard_data:
        for weakness in scorecard_data.get("weaknesses", []):
            if isinstance(weakness, str):
                weakness_check = check_for_bias(weakness)
                if not weakness_check["passed"]:
                    bias_results.append({
                        "field": "weaknesses",
                        "result": weakness_check,
                    })
    
    return {
        "passed": len(bias_results) == 0,
        "bias_results": bias_results,
        "total_flags": sum(len(r["result"]["flags"]) for r in bias_results),
    }


def apply_safety_constraints(data: dict[str, Any]) -> dict[str, Any]:
    """
    Apply safety constraints to ensure data integrity and fairness.
    """
    safety_flags = []
    
    # Check for extreme scores that might indicate bias
    if "technical_score" in data:
        if data["technical_score"] == 0 or data["technical_score"] == 100:
            safety_flags.append({
                "type": "extreme_score",
                "field": "technical_score",
                "message": "Extreme scores (0 or 100) should be avoided",
            })
    
    # Check for missing justification
    if data.get("overall_score", 0) < 50 and not data.get("detailed_feedback"):
        safety_flags.append({
            "type": "missing_justification",
            "message": "Low scores require detailed feedback",
        })
    
    # Check recommendation consistency
    overall = data.get("overall_score", 0)
    recommendation = data.get("recommendation", "").lower()
    
    if overall >= 80 and recommendation in ["reject", "not recommended"]:
        safety_flags.append({
            "type": "inconsistent_recommendation",
            "message": "High score with negative recommendation",
        })
    elif overall <= 40 and recommendation in ["hire", "strongly recommend"]:
        safety_flags.append({
            "type": "inconsistent_recommendation",
            "message": "Low score with positive recommendation",
        })
    
    return {
        "passed": len(safety_flags) == 0,
        "flags": safety_flags,
    }
