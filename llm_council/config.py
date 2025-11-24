"""Centralized configuration and utilities for the LLM Council scaffold."""
from __future__ import annotations

import os
from typing import Any, MutableMapping, Sequence, TypeVar

import streamlit as st
from pydantic import BaseModel, Field

OPENROUTER_API_URL = os.getenv(
    "OPENROUTER_API_URL",
    "https://openrouter.ai/api/v1/chat/completions",
)
OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"
REQUEST_TIMEOUT_SECONDS = 45
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2.0


class ParticipantModel(BaseModel):
    """Describes an individual model participating in the council."""

    role: str
    model: str
    temperature: float = Field(default=0.4, ge=0.0, le=2.0)
    system_prompt: str = Field(default="")

    class Config:
        frozen = True


DEFAULT_PARTICIPANTS: tuple[ParticipantModel, ...] = (
    ParticipantModel(
        role="Visionary Strategist",
        model="openrouter/openai/gpt-4o-mini",
        temperature=0.6,
        system_prompt="Map bold opportunities and highlight blue-sky scenarios.",
    ),
    ParticipantModel(
        role="Risk Analyst",
        model="openrouter/anthropic/claude-3-haiku",
        temperature=0.2,
        system_prompt="Identify failure modes, ethical pitfalls, and blind spots.",
    ),
    ParticipantModel(
        role="Customer Advocate",
        model="openrouter/google/gemini-1.5-flash",
        temperature=0.5,
        system_prompt="Channel real-user needs and prioritize simplicity.",
    ),
)

DEFAULT_CHAIRMAN_MODEL = ParticipantModel(
    role="Chairperson",
    model="openrouter/meta-llama/llama-3.1-70b-instruct",
    temperature=0.3,
    system_prompt=(
        "Moderate the council, synthesize diverse opinions, and push for consensus."
    ),
)

T = TypeVar("T")
_FALLBACK_SESSION_STATE: dict[str, Any] = {}


def _session_state() -> MutableMapping[str, Any]:
    """Return a Streamlit session state proxy with a local fallback."""

    try:
        return st.session_state
    except Exception:  # pragma: no cover - Streamlit runtime guards
        return _FALLBACK_SESSION_STATE


def get_or_init_session_state(key: str, default: T) -> T:
    """Return a session value, seeding it with *default* if unset."""

    state = _session_state()
    if key not in state:
        state[key] = default
    return state[key]


def persist_user_selections(key: str, selections: Sequence[str]) -> list[str]:
    """Persist the user's latest selections in session state."""

    state = _session_state()
    state[key] = list(selections)
    return state[key]


def _get_secret_from_streamlit(key: str) -> str | None:
    """Safely fetch a key from Streamlit secrets if available."""

    try:
        return st.secrets.get(key)  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - depends on Streamlit runtime
        return None


def get_openrouter_api_key(require: bool = True) -> str | None:
    """Return the OpenRouter API key from env vars or Streamlit secrets."""

    api_key = os.getenv(OPENROUTER_API_KEY_ENV)
    if not api_key:
        api_key = _get_secret_from_streamlit(OPENROUTER_API_KEY_ENV)

    if api_key:
        return api_key

    if require:
        raise RuntimeError(
            "OpenRouter API key missing. Set OPENROUTER_API_KEY or define it in "
            "Streamlit secrets."
        )
    return None


__all__ = [
    "OPENROUTER_API_URL",
    "OPENROUTER_API_KEY_ENV",
    "REQUEST_TIMEOUT_SECONDS",
    "MAX_RETRIES",
    "RETRY_BACKOFF_SECONDS",
    "ParticipantModel",
    "DEFAULT_PARTICIPANTS",
    "DEFAULT_CHAIRMAN_MODEL",
    "get_openrouter_api_key",
    "get_or_init_session_state",
    "persist_user_selections",
]
