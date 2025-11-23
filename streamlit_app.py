"""
Loyalty Program Evaluator - Streamlit Application

A beautiful web interface for evaluating loyalty programs using AI.
Features custom CSS, glassmorphism effects, and the Bricolage Grotesque font.

RECOMMENDED VERSION: Includes a Plotly Radar Chart for enhanced visualization.
"""

import json
import re
import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
import httpx
import streamlit as st
import pandas as pd
import plotly.graph_objects as go # Recommended addition for Radar Chart

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Petron | Loyalty Program Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------
# Custom CSS & Fonts
# ---------------------------
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&display=swap" rel="stylesheet">
    
    <style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
    
    /* Global Styles */
    * {
        font-family: 'Bricolage Grotesque', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container - Elegant light cream gradient */
    .main {
        background: linear-gradient(135deg, #f5f5f0 0%, #faf8f3 50%, #fff9f0 100%);
        padding-top: 160px;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 2rem;
        min-height: 100vh;
    }
    
    /* Streamlit default elements */
    .stApp {
        background: linear-gradient(135deg, #f5f5f0 0%, #faf8f3 50%, #fff9f0 100%);
    }
    
    /* Sticky Header Container - Compact and refined */
    .sticky-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1001;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 248, 243, 0.98) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 1.8rem 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(218, 165, 32, 0.1);
        border-bottom: 2px solid rgba(218, 165, 32, 0.2);
    }
    
    /* Header styling - Refined sophisticated branding */
    .main-header {
        font-family: 'Bricolage Grotesque', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #b8860b 0%, #daa520 50%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.4rem;
        letter-spacing: 0.12em;
        font-variant: small-caps;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .sub-header {
        font-family: 'Bricolage Grotesque', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: #4a5568;
        text-align: center;
        margin-bottom: 0;
        letter-spacing: 0.15em;
        font-variant: small-caps;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Glass card effect - Premium sophistication */
    .glass-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(255, 255, 255, 0.75) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 28px;
        border: 1.5px solid rgba(218, 165, 32, 0.18);
        padding: 3rem;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(218, 165, 32, 0.06);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12), 0 8px 20px rgba(218, 165, 32, 0.12);
        border-color: rgba(218, 165, 32, 0.35);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.8) 100%);
    }
    
    /* Score badge - Luxurious premium styling */
    .score-badge {
        display: inline-block;
        padding: 1rem 2.5rem;
        border-radius: 70px;
        font-weight: 800;
        font-size: 3rem;
        margin: 2rem 0;
        background: linear-gradient(135deg, rgba(218, 165, 32, 0.1) 0%, rgba(255, 215, 0, 0.06) 100%);
        backdrop-filter: blur(16px);
        border: 2.5px solid rgba(218, 165, 32, 0.25);
        box-shadow: 0 12px 32px rgba(218, 165, 32, 0.12), inset 0 2px 4px rgba(255, 255, 255, 0.6);
        animation: pulse 4s ease-in-out infinite;
        color: #2d3748;
        letter-spacing: 0.02em;
    }
    
    .score-excellent {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        border-color: rgba(46, 204, 113, 0.4);
        box-shadow: 0 8px 24px rgba(46, 204, 113, 0.25);
    }
    
    .score-good {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border-color: rgba(52, 152, 219, 0.4);
        box-shadow: 0 8px 24px rgba(52, 152, 219, 0.25);
    }
    
    .score-moderate {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        border-color: rgba(243, 156, 18, 0.4);
        box-shadow: 0 8px 24px rgba(243, 156, 18, 0.25);
    }
    
    .score-poor {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border-color: rgba(231, 76, 60, 0.4);
        box-shadow: 0 8px 24px rgba(231, 76, 60, 0.25);
    }
    
    .score-failing {
        background: linear-gradient(135deg, #c0392b 0%, #922b21 100%);
        color: white;
        border-color: rgba(192, 57, 43, 0.4);
        box-shadow: 0 8px 24px rgba(192, 57, 43, 0.25);
    }
    
    /* Parameter cards - Refined premium elegance */
    .param-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.88) 0%, rgba(255, 255, 255, 0.68) 100%);
        backdrop-filter: blur(14px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.2rem 0;
        border-left: 4px solid rgba(218, 165, 32, 0.5);
        border: 1.5px solid rgba(218, 165, 32, 0.12);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
    }
    
    .param-card:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(255, 255, 255, 0.78) 100%);
        border-left-color: rgba(218, 165, 32, 0.85);
        border-color: rgba(218, 165, 32, 0.28);
        transform: translateX(10px);
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08), -6px 0 16px rgba(218, 165, 32, 0.1);
    }
    
    .param-title {
        font-weight: 700;
        font-size: 1.18rem;
        color: #2d3748;
        margin-bottom: 0.6rem;
        letter-spacing: 0.01em;
    }
    
    .param-score {
        font-size: 1.7rem;
        font-weight: 800;
        background: linear-gradient(135deg, #b8860b 0%, #daa520 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.02em;
    }
    
    /* Action cards - Ultra-premium design */
    .action-card {
        background: linear-gradient(135deg, rgba(218, 165, 32, 0.09) 0%, rgba(255, 215, 0, 0.04) 100%);
        backdrop-filter: blur(14px);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        border: 1.5px solid rgba(218, 165, 32, 0.22);
        color: #2d3748;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
    }
    
    .action-card:hover {
        transform: translateY(-6px) scale(1.015);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1), 0 6px 16px rgba(218, 165, 32, 0.15);
        border-color: rgba(218, 165, 32, 0.4);
        background: linear-gradient(135deg, rgba(218, 165, 32, 0.13) 0%, rgba(255, 215, 0, 0.07) 100%);
    }
    
    .action-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #daa520 0%, #ffd700 100%);
        border-radius: 50%;
        font-weight: 800;
        margin-right: 1.5rem;
        font-size: 1.4rem;
        color: white;
        box-shadow: 0 6px 16px rgba(218, 165, 32, 0.25);
    }
    
    /* Material Icons */
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 24px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        vertical-align: middle;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.03);
        }
    }
    
    /* Streamlit specific overrides - Elegant inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
        backdrop-filter: blur(12px);
        border: 1.5px solid rgba(218, 165, 32, 0.25);
        border-radius: 12px;
        color: #2d3748;
        font-family: 'Bricolage Grotesque', sans-serif;
        padding: 0.8rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(218, 165, 32, 0.5);
        box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.1), 0 4px 12px rgba(218, 165, 32, 0.15);
        background: rgba(255, 255, 255, 0.95);
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(74, 85, 104, 0.5);
    }
    
    /* Premium button styling */
    .stButton > button {
        background: linear-gradient(135deg, #daa520 0%, #ffd700 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.9rem 2.5rem;
        font-weight: 700;
        font-size: 1.15rem;
        font-family: 'Bricolage Grotesque', sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(218, 165, 32, 0.25);
        letter-spacing: 0.02em;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(218, 165, 32, 0.35);
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Sidebar styling - Light elegant */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(250, 248, 243, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 2px solid rgba(218, 165, 32, 0.15);
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #2d3748;
        font-family: 'Bricolage Grotesque', sans-serif;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div {
        color: #4a5568;
    }
    
    /* Progress bars - Gold accent */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #daa520 0%, #ffd700 100%);
    }
    
    /* Expander - Refined */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.6) 100%);
        border-radius: 12px;
        color: #2d3748;
        font-weight: 600;
        border: 1px solid rgba(218, 165, 32, 0.2);
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(218, 165, 32, 0.35);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.75) 100%);
    }
    
    /* Success/Info/Warning boxes - Elegant */
    .stSuccess, .stInfo, .stWarning {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.6) 100%);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        border-left: 4px solid;
        color: #2d3748;
    }
    
    /* Radio buttons - Gold accent */
    .stRadio > div {
        gap: 1rem;
    }
    
    .stRadio > div > label {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.7) 0%, rgba(255, 255, 255, 0.5) 100%);
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        border: 1px solid rgba(218, 165, 32, 0.2);
        transition: all 0.3s ease;
        color: #2d3748;
    }
    
    .stRadio > div > label:hover {
        border-color: rgba(218, 165, 32, 0.4);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
    }
    
    /* Markdown text color */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #2d3748;
    }
    
    .main p, .main div, .main span {
        color: #4a5568;
    }
    
    /* Section headers with professional styling */
    .main h2 {
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(218, 165, 32, 0.15);
    }
    
    .main h3 {
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        color: #2d3748;
    }
    
    /* Info boxes - Professional styling */
    .stInfo {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.08) 0%, rgba(52, 152, 219, 0.05) 100%);
        border-left-color: #3498db;
        padding: 1rem 1.5rem;
    }
    
    /* Caption text */
    .stCaption {
        color: #718096;
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
    
    /* Horizontal rules */
    hr {
        border: none;
        border-top: 1px solid rgba(218, 165, 32, 0.15);
        margin: 2rem 0;
    }
    
    /* Download button special styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(218, 165, 32, 0.1) 0%, rgba(218, 165, 32, 0.05) 100%);
        color: #2d3748;
        border: 1.5px solid rgba(218, 165, 32, 0.3);
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, rgba(218, 165, 32, 0.15) 0%, rgba(218, 165, 32, 0.08) 100%);
        border-color: rgba(218, 165, 32, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(218, 165, 32, 0.2);
    }
    
    /* Footer - Elegant */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        color: #718096;
        font-size: 0.95rem;
        margin-top: 4rem;
        border-top: 1px solid rgba(218, 165, 32, 0.15);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# Configuration & Constants
# ---------------------------
OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", "gpt-4o-mini")
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

PARAM_WEIGHTS = {
    "earn_value": 15,
    "burn_value": 15,
    "physical_availability": 12,
    "mental_availability": 10,
    "frequency_engineering": 10,
    "data_personalisation": 10,
    "onboarding_activation": 8,
    "economics_governance": 7,
    "emotional_layer": 7,
    "partner_ecosystem": 6,
}

CLASS_BANDS = [
    (85, 100, "Market Leader Program", "score-excellent"),
    (70, 84.99, "High Performing Program", "score-good"),
    (55, 69.99, "Moderate / Underperforming Program", "score-moderate"),
    (40, 54.99, "Poor / Low Impact Program", "score-poor"),
    (0, 39.99, "Failing Program", "score-failing"),
]

ACTION_TEMPLATES = {
    "earn_value": "Increase earn rate on core purchase categories or introduce targeted bonus events to improve perceived value.",
    "burn_value": "Add flexible, frequent redemption options (small vouchers, partial redemptions) to reduce friction.",
    "physical_availability": "Expand redemption/earning footprint through partners or alternative channels (app, merchant POS).",
    "mental_availability": "Add simple branded touchpoints, reminders and high-frequency CTAs to increase recall.",
    "frequency_engineering": "Introduce habit mechanics (streaks, stamps, daily micro-rewards) to lift visit cadence.",
    "data_personalisation": "Segment users and deliver 1:1 offers using recency/frequency value buckets.",
    "onboarding_activation": "Give instant sign-up reward + checklist to ensure first 3 actions complete.",
    "economics_governance": "Tighten expiry/breakage policy, run controlled experiments and publish guardrails to protect unit economics.",
    "emotional_layer": "Add visible tiers, milestone notifications and social recognition for members.",
    "partner_ecosystem": "Add everyday-category partners (F&B, convenience) to increase utility and frequency.",
}

PARAM_NAMES = {
    "earn_value": "Earn Value / Value Pool",
    "burn_value": "Burn Value / Redemption",
    "physical_availability": "Physical Availability & Coverage",
    "mental_availability": "Mental Availability Integration",
    "frequency_engineering": "Frequency Engineering (Habit Loop)",
    "data_personalisation": "Data Utilisation / Personalisation Depth",
    "onboarding_activation": "Onboarding UX & Early Activation",
    "economics_governance": "Economics Governance",
    "emotional_layer": "Emotional Layer / Recognition",
    "partner_ecosystem": "Partner Ecosystem Depth & Relevance",
}

LLM_SYSTEM_PROMPT = r"""
You are a Loyalty Program Evaluator. The user will provide a loyalty program description (free text or partial JSON).
Produce EXACTLY one JSON object and nothing else. The JSON MUST contain keys: program_name, scores, rationales, concise_recommendations (optional), diagnostic_hint (optional).
- Scores must be integers 1..5 for each key: earn_value, burn_value, physical_availability, mental_availability, frequency_engineering, data_personalisation, onboarding_activation, economics_governance, emotional_layer, partner_ecosystem.
- Rationales must be <= 20 words each. If you infer anything due to missing info, begin rationale with "Inferred:".
- If you cannot determine a score, set it to 3 and mark the rationale with "Inferred:".
Return compact JSON only, no commentary.
"""

LLM_USER_PROMPT_TEMPLATE = r"""
Please analyze the following loyalty program description and OUTPUT ONLY the JSON object.

USER CONTENT:
---
{program_text}
---
Remember: output must be strict JSON. Use keys: program_name (string), scores (dict), rationales (dict), concise_recommendations (list, optional), diagnostic_hint (string, optional).
"""

# ---------------------------
# Utility Functions
# ---------------------------

def classify_program(score: float) -> tuple:
    """Returns (classification_label, css_class)"""
    for low, high, label, css_class in CLASS_BANDS:
        if low <= score <= high:
            return label, css_class
    return "Unclassified", "score-moderate"

def compute_success_index(param_scores_1_5: Dict[str, int]) -> Dict[str, Any]:
    results = []
    total = 0.0
    for key, weight in PARAM_WEIGHTS.items():
        raw_score = int(param_scores_1_5.get(key, 3))
        # Contribution is (Score / Max Score) * Weight
        contribution = raw_score * (weight / 5.0) 
        total += contribution
        results.append({
            "key": key,
            "weight": weight,
            "score_1_5": raw_score,
            "weighted": round(contribution, 2),
        })
    total_rounded = round(total, 1)
    classification, css_class = classify_program(total_rounded)
    return {
        "success_index": total_rounded,
        "classification": classification,
        "css_class": css_class,
        "parameter_scores": results,
    }

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Attempts to find the first JSON object in the text and parse it."""
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM output")
    candidate = text[start:end+1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        # Attempt to clean up common LLM JSON errors (like trailing commas)
        cleaned = re.sub(r',\s*([\]}])', r'\1', candidate)
        try:
            return json.loads(cleaned)
        except Exception as e2:
            raise ValueError(f"Failed to parse JSON from LLM output: {e2}") from e2

def safe_int_score(val: Any) -> int:
    """Ensures a value is an integer between 1 and 5 (inclusive), defaulting to 3."""
    try:
        vi = int(val)
    except Exception:
        vi = 3
    if vi < 1: vi = 1
    if vi > 5: vi = 5
    return vi

async def call_openrouter(program_text: str, retries: int = 2, timeout: int = 30) -> Dict[str, Any]:
    """Calls OpenRouter chat completions and returns the parsed JSON LLM payload."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": LLM_SYSTEM_PROMPT},
            {"role": "user", "content": LLM_USER_PROMPT_TEMPLATE.format(program_text=program_text)}
        ],
        "max_tokens": 800,
        "temperature": 0.0
    }

    backoff = 1.0
    last_error = None
    
    # Use trust_env=True to respect system proxy settings (HTTP_PROXY, HTTPS_PROXY env vars)
    async with httpx.AsyncClient(timeout=timeout, trust_env=True) as client:
        for attempt in range(retries + 1):
            try:
                resp = await client.post(OPENROUTER_CHAT_URL, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                
                content = None
                if isinstance(data, dict):
                    choices = data.get("choices")
                    if choices and isinstance(choices, list) and len(choices) > 0:
                        m = choices[0].get("message") or choices[0]
                        if isinstance(m, dict):
                            content = m.get("content") or m.get("message") or None
                    if not content:
                        content = data.get("output") or data.get("text") or None
                if not content and isinstance(data, str):
                    content = data
                if not content:
                    raise ValueError("No textual content found in model response")

                parsed = extract_json_from_text(content)
                return parsed
            except httpx.ConnectError as e:
                last_error = e
                error_msg = str(e)
                if "getaddrinfo failed" in error_msg or "11001" in error_msg:
                    raise ConnectionError(
                        f"Network error: Cannot connect to OpenRouter API. "
                        f"Please check your internet connection, proxy settings, or firewall. "
                        f"URL: {OPENROUTER_CHAT_URL}"
                    ) from e
                if attempt < retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise ConnectionError(f"Failed to connect to OpenRouter API after {retries + 1} attempts: {error_msg}") from e
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 401:
                    raise ValueError("Invalid API key. Please check your OPENROUTER_API_KEY in secrets.toml") from e
                elif e.response.status_code == 429:
                    raise ValueError("Rate limit exceeded. Please try again later.") from e
                else:
                    raise ValueError(f"HTTP error {e.response.status_code}: {e.response.text}") from e
            except Exception as e:
                last_error = e
                if attempt < retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise
    
    if last_error:
        raise last_error

# --- NEW RECOMMENDED FUNCTION ---
def create_radar_chart(parameter_data: List[Dict[str, Any]], program_name: str) -> go.Figure:
    """Creates a Plotly Radar Chart from the parameter scores."""
    
    # Extract data for the chart
    categories = [PARAM_NAMES[d['key']] for d in parameter_data]
    scores = [d['score_1_5'] for d in parameter_data]
    
    # Dataframe structure for Plotly
    df = pd.DataFrame(dict(
        r=scores,
        theta=categories
    ))

    # --- Create Plotly Figure ---
    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=df['r'],
                theta=df['theta'],
                fill='toself',
                name=program_name,
                line_color='#daa520', # Gold
                marker_color='#b8860b',
                opacity=0.6,
                hoverinfo='text',
                text=[f"Score: {s}/5" for s in scores]
            )
        ],
        layout=go.Layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickvals=[1, 2, 3, 4, 5],
                    ticktext=['1 (Failing)', '2 (Poor)', '3 (Moderate)', '4 (Good)', '5 (Excellent)'],
                    gridcolor='rgba(218, 165, 32, 0.15)'
                ),
                angularaxis=dict(
                    rotation=90,
                    direction='clockwise',
                ),
            ),
            showlegend=False,
            title=dict(
                text=f'**{program_name}** Performance Breakdown (Score 1-5)',
                font=dict(family='Bricolage Grotesque', size=16, color='#2d3748')
            ),
            # Transparent background to blend with glassmorphism
            paper_bgcolor='rgba(255, 255, 255, 0)', 
            plot_bgcolor='rgba(255, 255, 255, 0)',
            height=600 
        )
    )
    
    # Style the text in the figure
    fig.update_layout(font_family="Bricolage Grotesque", font_color="#4a5568")
    
    return fig


# ---------------------------
# Main Application
# ---------------------------

def main():
    # Sticky Header
    st.markdown('''
    <div class="sticky-header">
        <h1 class="main-header">Petron</h1>
        <p class="sub-header">Loyalty Program Analytics Platform</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Check API key
    if not OPENROUTER_KEY or OPENROUTER_KEY == "your-api-key-here":
        st.error("Configuration Required: Please configure your OPENROUTER_API_KEY in `.streamlit/secrets.toml`")
        st.stop()
    
    # Welcome section with professional guidance
    if 'analysis_run' not in st.session_state:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(52, 152, 219, 0.08) 0%, rgba(52, 152, 219, 0.05) 100%);
                    border-left: 3px solid #3498db;
                    padding: 1rem 1.5rem;
                    border-radius: 8px;
                    margin-bottom: 1rem;'>
            <p style='font-size: 0.85rem; color: #4a5568; margin: 0;'>
                <strong style='font-size: 0.9rem;'>Welcome to Petron Analytics</strong><br><br>
                This platform evaluates loyalty programs across 10 key performance parameters using advanced AI analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Evaluation Framework - Collapsible
    with st.expander("Evaluation Framework & Methodology", expanded=False):
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(218, 165, 32, 0.05) 0%, rgba(218, 165, 32, 0.02) 100%); 
                    padding: 1rem; border-radius: 8px; border-left: 3px solid rgba(218, 165, 32, 0.4);'>
        <p style='color: #4a5568; margin-bottom: 1rem;'>
        Our proprietary AI model analyzes loyalty programs across 10 critical performance parameters, 
        each weighted by industry impact and strategic importance.
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        params_list = list(PARAM_NAMES.items())
        
        for idx, (key, name) in enumerate(params_list):
            weight = PARAM_WEIGHTS[key]
            with col1 if idx < 5 else col2:
                st.markdown(f"**{name}**")
                st.caption(f"Weight: {weight}%")
        
        st.markdown("---")
        st.caption(f"**Model:** {OPENROUTER_MODEL} | **Status:** Connected")
    
    # Main input section
    st.markdown("### Program Information")
    st.markdown("<p style='color: #718096; font-size: 0.9rem; margin-top: -0.5rem;'>Provide detailed information about your loyalty program for accurate analysis</p>", unsafe_allow_html=True)
    
    input_method = st.radio(
        "Choose input method:",
        ["Text Description", "JSON Format"],
        horizontal=True
    )
    
    program_text = ""
    
    if input_method == "Text Description":
        program_text = st.text_area(
            "Describe your loyalty program:",
            height=200,
            placeholder="Example: Our loyalty program offers 1 point per dollar spent. Members can redeem points for discounts. We have 500 partner locations...",
            help="Provide as much detail as possible about your loyalty program",
            max_chars=5000
        )
        if program_text:
            char_count = len(program_text)
            st.caption(f"Characters: {char_count}/5000")
    else:
        program_json = st.text_area(
            "Paste your program JSON:",
            height=200,
            placeholder='{"program_name": "MyProgram", "features": {...}}',
            help="Paste a JSON object describing your program"
        )
        if program_json:
            try:
                json.loads(program_json)  # Validate JSON
                program_text = program_json
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your input.")
    
    # Evaluate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        evaluate_btn = st.button("Run Analysis", use_container_width=True, type="primary")
    
    # Process evaluation
    if evaluate_btn and program_text:
        with st.spinner("Analyzing program data... This may take a few moments."):
            # Set session state to track analysis
            st.session_state['analysis_run'] = True
            try:
                # Call LLM
                llm_out = asyncio.run(call_openrouter(program_text))
                
                # Extract data
                program_name = llm_out.get("program_name", "Unnamed Program")
                scores_raw = llm_out.get("scores", {})
                rationales_raw = llm_out.get("rationales", {})
                concise_recs = llm_out.get("concise_recommendations", [])
                diagnostic_hint = llm_out.get("diagnostic_hint", "")
                
                # Normalize scores
                scores = {}
                for key in PARAM_WEIGHTS.keys():
                    scores[key] = safe_int_score(scores_raw.get(key, 3))
                
                # Normalize rationales
                rationales = {}
                for key in PARAM_WEIGHTS.keys():
                    val = rationales_raw.get(key)
                    if not val:
                        rationales[key] = "Inferred: insufficient detail"
                    else:
                        rationales[key] = val.strip()[:120]
                
                # Compute success index
                computed = compute_success_index(scores)
                
                # Compute deltas (Potential Impact)
                base_success = computed["success_index"]
                deltas = []
                for key in PARAM_WEIGHTS.keys():
                    cur = scores.get(key, 3)
                    if cur >= 5:
                        delta = 0.0
                    else:
                        tmp_scores = dict(scores)
                        tmp_scores[key] = cur + 1
                        new_total = compute_success_index(tmp_scores)["success_index"]
                        delta = round(new_total - base_success, 1)
                    deltas.append({"key": key, "delta_if_plus1": delta})
                
                # Top 3 fixes
                sorted_deltas = sorted(deltas, key=lambda x: x["delta_if_plus1"], reverse=True)
                top3_keys = [d["key"] for d in sorted_deltas[:3]]
                
                # Display results
                st.markdown("---")
                st.markdown(f'<h2 style="color: #2d3748;"><span class="material-symbols-outlined" style="vertical-align: middle; font-size: 1.8rem; margin-right: 0.5rem;">analytics</span>Analysis Results: {program_name}</h2>', unsafe_allow_html=True)
                
                # Success Index
                st.markdown(f"""
                <div style="text-align: center; margin: 2rem 0;">
                    <h3 style="color: #2d3748; margin-bottom: 1rem;">Success Index</h3>
                    <div class="score-badge {computed['css_class']}">
                        {computed['success_index']}
                    </div>
                    <h4 style="color: #2d3748; margin-top: 1rem;">{computed['classification']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # --- START NEW RADAR CHART INTEGRATION ---
                st.markdown(f'''
                <div class="glass-card" style="padding: 2rem 1.5rem; margin-top: 0;">
                    <h3 style="color: #2d3748; text-align: center; margin-top: 0; margin-bottom: 0.5rem;">
                        <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 1.6rem; margin-right: 0.4rem;">radar</span>Strategic Performance Radar
                    </h3>
                </div>
                ''', unsafe_allow_html=True)
                
                # Generate and display the chart
                radar_fig = create_radar_chart(computed["parameter_scores"], program_name)
                st.plotly_chart(radar_fig, use_container_width=True, config={'displayModeBar': False})
                # --- END NEW RADAR CHART INTEGRATION ---

                # Diagnostic hint
                if diagnostic_hint:
                    st.info(f"**Key Insight:** {diagnostic_hint}")
                
                # Top 3 Recommended Actions
                st.markdown('<h3 style="color: #2d3748;"><span class="material-symbols-outlined" style="vertical-align: middle; font-size: 1.4rem; margin-right: 0.4rem;">priority_high</span>Priority Recommendations</h3>', unsafe_allow_html=True)
                for idx, key in enumerate(top3_keys, 1):
                    st.markdown(f"""
                    <div class="action-card">
                        <span class="action-number">{idx}</span>
                        <strong>{PARAM_NAMES[key]}</strong>
                        <p style="margin-top: 0.5rem; margin-bottom: 0;">{ACTION_TEMPLATES[key]}</p>
                        <p style="margin-top: 0.5rem; color: #daa520; font-weight: 600;">
                            Potential Impact: +{[d for d in deltas if d['key'] == key][0]['delta_if_plus1']} points
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Parameter Breakdown
                st.markdown('<h3 style="color: #2d3748;"><span class="material-symbols-outlined" style="vertical-align: middle; font-size: 1.4rem; margin-right: 0.4rem;">bar_chart</span>Detailed Parameter Analysis</h3>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                for idx, (key, name) in enumerate(PARAM_NAMES.items()):
                    score = scores[key]
                    weight = PARAM_WEIGHTS[key]
                    rationale = rationales[key]
                    
                    with col1 if idx % 2 == 0 else col2:
                        with st.expander(f"**{name}** - Score: {score}/5"):
                            st.markdown(f"**Weight:** {weight}%")
                            st.progress(score / 5.0)
                            st.markdown(f"**Rationale:** {rationale}")
                            
                            # Show potential impact
                            delta = [d for d in deltas if d['key'] == key][0]['delta_if_plus1']
                            if delta > 0:
                                st.markdown(f"**Potential Impact:** +{delta} points if improved to a score of {score + 1}")
                
                # Additional recommendations
                if concise_recs:
                    st.markdown('<h3 style="color: #2d3748;"><span class="material-symbols-outlined" style="vertical-align: middle; font-size: 1.4rem; margin-right: 0.4rem;">lightbulb</span>Additional Insights</h3>', unsafe_allow_html=True)
                    for rec in concise_recs:
                        st.markdown(f"- {rec}")
                
                # Export option
                st.markdown("---")
                st.markdown('<h3 style="color: #2d3748;"><span class="material-symbols-outlined" style="vertical-align: middle; font-size: 1.4rem; margin-right: 0.4rem;">download</span>Export Report</h3>', unsafe_allow_html=True)
                
                export_data = {
                    "program_name": program_name,
                    "success_index": computed["success_index"],
                    "classification": computed["classification"],
                    "scores": scores,
                    "rationales": rationales,
                    "top_3_actions": [ACTION_TEMPLATES[k] for k in top3_keys],
                    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                }
                
                st.download_button(
                    label="Download Report (JSON)",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"loyalty_eval_{program_name.replace(' ', '_')}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"Analysis Error: {str(e)}")
                st.exception(e)
    
    elif evaluate_btn and not program_text:
        st.warning("Please enter program details before running the analysis.")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Powered by AI • Built with Streamlit • Designed with ❤️</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":

    main()

