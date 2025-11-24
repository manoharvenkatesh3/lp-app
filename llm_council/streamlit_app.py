"""Minimal Streamlit entrypoint for the LLM Council scaffold."""
from __future__ import annotations

from typing import List

import streamlit as st

from config import (
    DEFAULT_CHAIRMAN_MODEL,
    DEFAULT_PARTICIPANTS,
    get_openrouter_api_key,
    get_or_init_session_state,
    persist_user_selections,
)

st.set_page_config(
    page_title="LLM Council",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def _build_participant_summary(selected_roles: List[str]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for participant in DEFAULT_PARTICIPANTS:
        if participant.role in selected_roles:
            summaries.append(participant.model_dump())
    return summaries


def main() -> None:
    st.title("LLM Council")
    st.caption(
        "Scaffold a multi-model deliberation experience with reusable config and state helpers."
    )

    api_key = get_openrouter_api_key(require=False)
    if api_key:
        st.success("OpenRouter API key detected. Ready to orchestrate calls when implemented.")
    else:
        st.warning(
            "No OpenRouter API key detected. Export OPENROUTER_API_KEY or add it to "
            "Streamlit secrets to enable API calls."
        )

    participant_roles = [participant.role for participant in DEFAULT_PARTICIPANTS]
    default_selection = get_or_init_session_state("selected_participants", participant_roles)

    selected_roles = st.multiselect(
        "Choose the models that should attend today's council",
        participant_roles,
        default=default_selection,
    )

    persist_user_selections("selected_participants", selected_roles)

    st.subheader("Participant configuration")
    if selected_roles:
        st.json(_build_participant_summary(selected_roles), expanded=False)
    else:
        st.info("Select at least one participant to inspect their configuration.")

    st.subheader("Chairperson model")
    st.json(DEFAULT_CHAIRMAN_MODEL.model_dump(), expanded=False)

    st.markdown(
        "This starter view intentionally avoids making network calls so that you can "
        "layer in orchestration, httpx clients, and council logic incrementally."
    )


if __name__ == "__main__":
    main()
