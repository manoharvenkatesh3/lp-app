"""Eureka - AI Talent Discovery Engine

A polished enterprise UI for AI-powered resume screening, ranking, and monitoring.
"""
from __future__ import annotations

import json
from typing import Dict, Optional

import pandas as pd
import streamlit as st

from .constants import (
    DEFAULT_SCREEN_CONFIG,
    REQUIRED_FIELDS,
    WORK_MODELS,
    load_default_candidates,
)
from .css_styles import apply_custom_css
from .utils import (
    apply_column_mapping,
    chunked,
    compute_summary_metrics,
    fetch_google_sheet,
    parse_uploaded_file,
    score_candidates,
    top_candidates,
)

st.set_page_config(
    page_title="Eureka | AI Talent Discovery Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(apply_custom_css(), unsafe_allow_html=True)

st.markdown(
    """
    <div class="eureka-fixed-header-container">
        <h1 class="eureka-main-header">🔍 EUREKA</h1>
        <p class="eureka-sub-header">AI Talent Discovery Engine · Enterprise Recruiting Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Centralized session state initialization."""
    if "candidates_df" not in st.session_state:
        st.session_state["candidates_df"] = load_default_candidates()
    if "scored_df" not in st.session_state:
        st.session_state["scored_df"] = None
    if "screen_config" not in st.session_state:
        st.session_state["screen_config"] = DEFAULT_SCREEN_CONFIG.copy()
    if "ingestion_status" not in st.session_state:
        st.session_state["ingestion_status"] = []


def set_ingestion_status(steps):
    st.session_state["ingestion_status"] = steps


def render_processing_status():
    st.markdown("### 📡 Processing Status")
    with st.container():
        st.markdown('<div class="screening-box">', unsafe_allow_html=True)
        statuses = st.session_state.get("ingestion_status", [])
        if not statuses:
            st.markdown(
                "<p style='margin:0;'>Awaiting ingestion events.</p>",
                unsafe_allow_html=True,
            )
        else:
            for status in statuses:
                label = status.get("label", "Processing")
                progress_value = int(status.get("progress", 0))
                st.progress(progress_value)
                st.caption(label)
        st.markdown("</div>", unsafe_allow_html=True)


def tab_load_candidates():

    """Tab 1: Data Ingestion (Local Upload + Google Sheets)."""
    st.markdown("### 📥 Load Candidates")
    st.caption("Ingest candidate data from multiple sources")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        with st.expander("📂 Local Resume Upload", expanded=False):
            st.caption("Upload CSV, Excel, or JSON files with candidate resumes")
            uploaded_file = st.file_uploader(
                "Choose file",
                type=["csv", "xlsx", "xls", "json"],
                help="Supported formats: CSV, XLSX, XLS, JSON",
                label_visibility="collapsed",
            )

            if uploaded_file is not None:
                if st.button("🔄 Process Local File", use_container_width=True, type="primary"):
                    with st.spinner("Processing local file..."):
                        try:
                            raw_df = parse_uploaded_file(uploaded_file)
                            st.session_state["raw_upload"] = raw_df
                            set_ingestion_status(
                                [
                                    {"label": "Upload received", "progress": 40},
                                    {"label": "Awaiting column mapping", "progress": 60},
                                ]
                            )
                            st.success(f"✓ Loaded {len(raw_df)} records from {uploaded_file.name}")
                            with st.expander("📊 Preview Raw Data"):
                                st.data_editor(
                                    raw_df.head(5),
                                    disabled=True,
                                    use_container_width=True,
                                )
                        except Exception as exc:
                            st.error(f"❌ File Error: {exc}")

    with col2:
        st.markdown("**🌐 Google Sheets Data Import**")
        st.caption("Load candidates directly from a published Google Sheet")
        sheet_url = st.text_input(
            "Google Sheets URL or Spreadsheet ID",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Ensure the sheet is published or publicly accessible",
        )

        if sheet_url.strip():
            if st.button("📥 Load from Google Sheets", use_container_width=True, type="primary"):
                with st.spinner("Fetching Google Sheets data..."):
                    try:
                        raw_df = fetch_google_sheet(sheet_url)
                        st.session_state["raw_upload"] = raw_df
                        set_ingestion_status(
                            [
                                {"label": "Sheets data fetched", "progress": 40},
                                {"label": "Awaiting column mapping", "progress": 60},
                            ]
                        )
                        st.success(f"✓ Loaded {len(raw_df)} records from Google Sheets")
                        with st.expander("📊 Preview Raw Data"):
                            st.data_editor(
                                raw_df.head(5),
                                disabled=True,
                                use_container_width=True,
                            )
                    except Exception as exc:
                        st.error(f"❌ Google Sheets Error: {exc}")

    if "raw_upload" in st.session_state:
        st.markdown("---")
        st.markdown("### 🗂️ Column Mapping")
        st.caption("Map uploaded columns to Eureka standard fields")

        raw_df = st.session_state["raw_upload"]
        available_cols = [""] + list(raw_df.columns)

        mapping: Dict[str, Optional[str]] = {}
        cols = st.columns(3)
        for idx, (key, display_name) in enumerate(REQUIRED_FIELDS.items()):
            with cols[idx % 3]:
                mapping[key] = st.selectbox(
                    display_name,
                    available_cols,
                    key=f"mapping_{key}",
                )

        col_load_1, col_load_2, col_load_3 = st.columns([1, 2, 1])
        with col_load_2:
            if st.button("✅ Apply Mapping & Load Candidates", use_container_width=True, type="primary"):
                with st.container():
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()

                    try:
                        progress_placeholder.progress(0.2)
                        status_placeholder.info("⏳ Validating columns...")
                        normalized_df = apply_column_mapping(raw_df, mapping)

                        progress_placeholder.progress(0.6)
                        status_placeholder.info("⏳ Normalizing data...")
                        st.session_state["candidates_df"] = normalized_df
                        st.session_state["scored_df"] = None

                        progress_placeholder.progress(1.0)
                        status_placeholder.success(f"✅ Successfully loaded {len(normalized_df)} candidates!")

                        set_ingestion_status(
                            [
                                {"label": "Mapping applied", "progress": 80},
                                {"label": "Load complete!", "progress": 100},
                            ]
                        )

                        st.balloons()
                        del st.session_state["raw_upload"]

                    except Exception as exc:
                        status_placeholder.error(f"❌ Load Error: {exc}")
                        set_ingestion_status(
                            [
                                {"label": "Error during load", "progress": 20},
                            ]
                        )

        with st.expander("📋 Current Data Preview (Data Editor)", expanded=False):
            st.data_editor(
                st.session_state.get("candidates_df", pd.DataFrame()),
                disabled=True,
                use_container_width=True,
                height=300,
            )

    render_processing_status()


def tab_view_candidates():
    """Tab 2: Data Overview with Metrics and Enhanced Dataframe."""
    st.markdown("### 👥 View Candidates")
    st.caption("Overview of loaded candidate profiles")

    df = st.session_state.get("candidates_df", pd.DataFrame())

    if df.empty:
        st.info("ℹ️ No candidate data loaded. Use **Tab 1** to import candidates.")
        return

    metrics = compute_summary_metrics(df)

    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        st.metric(
            "Total Candidates",
            metrics["total"],
            delta=None,
            help="Total number of loaded candidates",
        )

    with col2:
        st.metric(
            "Avg Experience",
            f"{metrics['average_experience']} yrs",
            delta=None,
            help="Average years of experience",
        )

    with col3:
        st.metric(
            "Immediate Ready",
            metrics["immediate_ready"],
            delta=None,
            help="Candidates available immediately",
        )

    with col4:
        st.metric(
            "Remote Ready",
            metrics["remote_ready"],
            delta=None,
            help="Candidates open to remote roles",
        )

    st.markdown("---")
    st.markdown("### 📊 Candidates Data Table")

    column_config = {
        "id": st.column_config.TextColumn(
            "ID",
            width="small",
            pinned=True,
        ),
        "full_name": st.column_config.TextColumn(
            "Full Name",
            width="medium",
        ),
        "email": st.column_config.TextColumn(
            "Email",
            width="medium",
        ),
        "current_role": st.column_config.TextColumn(
            "Current Role",
            width="medium",
        ),
        "experience_years": st.column_config.NumberColumn(
            "Experience (yrs)",
            format="%.1f",
            width="small",
        ),
        "skills": st.column_config.ListColumn(
            "Skills",
            width="large",
            help="Key skills and competencies",
        ),
        "work_model": st.column_config.TextColumn(
            "Work Model",
            width="small",
        ),
        "location": st.column_config.TextColumn(
            "Location",
            width="medium",
        ),
    }

    st.data_editor(
        df,
        column_config=column_config,
        disabled=True,
        use_container_width=True,
        height=500,
        hide_index=True,
    )


def tab_screen_and_rank():
    """Tab 3: Screen & Rank Configuration."""
    st.markdown("### 🎯 Screen & Rank")
    st.caption("Define job requirements and scoring weights")

    col_jd, col_weights = st.columns([2, 1], gap="large")

    with col_jd:
        st.markdown("#### 📋 Job Description")
        job_title = st.text_input(
            "Job Title",
            value=st.session_state["screen_config"]["job_title"],
            placeholder="e.g., Senior AI Recruiter",
        )

        job_description = st.text_area(
            "Job Description",
            value=st.session_state["screen_config"]["job_description"],
            height=200,
            placeholder="Paste full job description here...",
        )

        col_model, col_exp = st.columns(2)
        with col_model:
            preferred_work_model = st.selectbox(
                "Preferred Work Model",
                WORK_MODELS,
                index=WORK_MODELS.index(st.session_state["screen_config"]["preferred_work_model"]),
            )
        with col_exp:
            minimum_experience = st.number_input(
                "Minimum Experience (years)",
                min_value=0,
                max_value=30,
                value=st.session_state["screen_config"]["minimum_experience"],
                step=1,
            )

    with col_weights:
        st.markdown("#### ⚖️ Ranking Weights")
        st.caption("Adjust scoring criteria (must sum to 100%)")

        weights = st.session_state["screen_config"]["weights"]

        skills_weight = st.slider(
            "Skills Alignment",
            0,
            100,
            weights["skills_alignment"],
            step=5,
            help="Weight for skills match",
        )

        experience_weight = st.slider(
            "Experience Fit",
            0,
            100,
            weights["experience_fit"],
            step=5,
            help="Weight for experience level",
        )

        culture_weight = st.slider(
            "Culture Impact",
            0,
            100,
            weights["culture_impact"],
            step=5,
            help="Weight for cultural and work model fit",
        )

        total_weight = skills_weight + experience_weight + culture_weight

        if total_weight == 100:
            st.success(f"✅ Total: {total_weight}%")
        else:
            st.error(f"⚠️ Total: {total_weight}% (Must be 100%)")

    st.markdown("---")

    col_run_1, col_run_2, col_run_3 = st.columns([1, 2, 1])
    with col_run_2:
        can_run = total_weight == 100 and job_title.strip() and job_description.strip()
        if st.button(
            "🚀 Run Screening & Ranking",
            use_container_width=True,
            type="primary",
            disabled=not can_run,
        ):
            with st.spinner("Analyzing candidates..."):
                df = st.session_state.get("candidates_df", pd.DataFrame())
                if df.empty:
                    st.error("❌ No candidates loaded. Please load data in Tab 1.")
                else:
                    try:
                        config = {
                            "job_title": job_title,
                            "job_description": job_description,
                            "weights": {
                                "skills_alignment": skills_weight,
                                "experience_fit": experience_weight,
                                "culture_impact": culture_weight,
                            },
                            "preferred_work_model": preferred_work_model,
                            "minimum_experience": minimum_experience,
                        }
                        st.session_state["screen_config"] = config

                        scored_df = score_candidates(df, **config)
                        st.session_state["scored_df"] = scored_df

                        st.success(f"✅ Successfully ranked {len(scored_df)} candidates!")
                        st.balloons()

                    except Exception as exc:
                        st.error(f"❌ Ranking Error: {exc}")


def tab_monitoring_results():
    """Tab 4: Monitoring Results with Grid Layout."""
    st.markdown("### 📈 Monitoring Results")
    st.caption("Ranked candidates and detailed profiles")

    scored_df = st.session_state.get("scored_df")

    if scored_df is None or scored_df.empty:
        st.info("ℹ️ No screening results yet. Use **Tab 3** to run candidate screening.")
        return

    top_df = top_candidates(scored_df, limit=7)

    st.markdown("#### 🏆 Top 7 Candidates")
    st.caption("Highest-scoring profiles from the screening")

    if top_df.empty:
        st.warning("No top candidates found.")
        return

    rows = list(top_df.to_dict(orient="records"))
    for row_items in chunked(rows, 3):
        cols = st.columns(len(row_items))
        for idx, candidate in enumerate(row_items):
            with cols[idx]:
                rec = candidate.get("recommendation", "Pending")
                rec_class = (
                    "recommendation-strong"
                    if rec == "Strong"
                    else "recommendation-balanced" if rec == "Balanced" else "recommendation-watch"
                )
                st.markdown(
                    f"""
                    <div class="screening-box candidate-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h4 style="margin: 0; color: var(--text-primary);">{candidate.get("full_name", "Unknown")}</h4>
                            <span class="recommendation-badge {rec_class}">{rec}</span>
                        </div>
                        <p style="margin: 0.5rem 0; font-size: 0.9rem;"><strong>Score:</strong> {candidate.get("match_score", 0):.1f}</p>
                        <p style="margin: 0.5rem 0; font-size: 0.9rem;"><strong>Role:</strong> {candidate.get("current_role", "—")}</p>
                        <p style="margin: 0.5rem 0; font-size: 0.9rem;"><strong>Experience:</strong> {candidate.get("experience_years", 0)} years</p>
                        <p style="margin: 0.5rem 0; font-size: 0.9rem;"><strong>Location:</strong> {candidate.get("location", "—")}</p>
                        <p style="margin: 0.5rem 0; font-size: 0.9rem;"><strong>Work Model:</strong> {candidate.get("work_model", "—")}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.markdown("#### 📋 Full Rankings Table")

    column_config = {
        "id": st.column_config.TextColumn("ID", width="small", pinned=True),
        "full_name": st.column_config.TextColumn("Name", width="medium"),
        "match_score": st.column_config.ProgressColumn(
            "Match Score",
            format="%.1f",
            min_value=0,
            max_value=100,
            width="medium",
        ),
        "recommendation": st.column_config.TextColumn("Status", width="small"),
        "current_role": st.column_config.TextColumn("Role", width="medium"),
        "experience_years": st.column_config.NumberColumn("Experience", format="%.1f yrs", width="small"),
        "skills": st.column_config.ListColumn("Skills", width="large"),
        "work_model": st.column_config.TextColumn("Work Model", width="small"),
    }

    st.data_editor(
        scored_df,
        column_config=column_config,
        disabled=True,
        use_container_width=True,
        height=400,
        hide_index=True,
    )

    st.markdown("---")
    st.markdown("#### 🔍 Detailed Profile Viewer")

    selected_id = st.selectbox(
        "Select Candidate ID to View Details",
        scored_df["id"].tolist(),
    )

    if selected_id:
        candidate = scored_df[scored_df["id"] == selected_id].iloc[0].to_dict()
        rec = candidate.get("recommendation", "Pending")
        rec_class = (
            "recommendation-strong"
            if rec == "Strong"
            else "recommendation-balanced" if rec == "Balanced" else "recommendation-watch"
        )

        st.markdown(
            f"""
            <div class="screening-box">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: var(--text-primary);">{candidate.get("full_name", "Unknown")}</h3>
                    <span class="recommendation-badge {rec_class}">{rec}</span>
                </div>
                <hr style="margin: 1rem 0;">
                <p><strong>Match Score:</strong> {candidate.get("match_score", 0):.1f}</p>
                <p><strong>Current Role:</strong> {candidate.get("current_role", "—")}</p>
                <p><strong>Experience:</strong> {candidate.get("experience_years", 0)} years</p>
                <p><strong>Email:</strong> {candidate.get("email", "—")}</p>
                <p><strong>Location:</strong> {candidate.get("location", "—")}</p>
                <p><strong>Work Model:</strong> {candidate.get("work_model", "—")}</p>
                <p><strong>Availability:</strong> {candidate.get("availability", "—")}</p>
                <hr style="margin: 1rem 0;">
                <p><strong>Skills:</strong> {", ".join(candidate.get("skills", []))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("#### 💾 Export Results")

    export_data = {
        "screen_config": st.session_state.get("screen_config", {}),
        "top_candidates": top_df.to_dict(orient="records"),
        "all_rankings": scored_df.to_dict(orient="records"),
    }

    col_export_1, col_export_2, col_export_3 = st.columns([1, 2, 1])
    with col_export_2:
        st.download_button(
            label="📥 Download Rankings (JSON)",
            data=json.dumps(export_data, indent=2, default=str),
            file_name="eureka_results.json",
            mime="application/json",
            use_container_width=True,
        )


def render_sticky_tabs():
    """Render fixed/sticky tabs that don't scroll with content."""
    tab_options = [
        ("📥 Load Candidates", "load_candidates"),
        ("👥 View Candidates", "view_candidates"),
        ("🎯 Screen & Rank", "screen_and_rank"),
        ("📈 Monitoring Results", "monitoring_results"),
    ]

    if "current_tab" not in st.session_state:
        st.session_state["current_tab"] = "load_candidates"

    col_tabs = st.columns(len(tab_options), gap="small")
    for idx, (label, tab_key) in enumerate(tab_options):
        with col_tabs[idx]:
            if st.button(
                label,
                key=f"tab_{tab_key}",
                use_container_width=True,
                type="primary" if st.session_state["current_tab"] == tab_key else "secondary",
            ):
                st.session_state["current_tab"] = tab_key
                st.rerun()

    st.markdown("---")

    if st.session_state["current_tab"] == "load_candidates":
        tab_load_candidates()
    elif st.session_state["current_tab"] == "view_candidates":
        tab_view_candidates()
    elif st.session_state["current_tab"] == "screen_and_rank":
        tab_screen_and_rank()
    elif st.session_state["current_tab"] == "monitoring_results":
        tab_monitoring_results()


def main():
    initialize_session_state()
    render_sticky_tabs()


if __name__ == "__main__":
    main()
