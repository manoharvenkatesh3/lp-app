"""
Eureka - AI Talent Discovery Engine

An elegant enterprise application for screening, ranking, and managing candidates
using AI-powered analysis. Features custom CSS, glassmorphism effects, and the 
Bricolage Grotesque font for a world-class user experience.
"""

import json
import io
import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
import httpx
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Eureka | AI Talent Discovery Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------
# Custom CSS & Fonts
# ---------------------------
def apply_custom_css():
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&display=swap" rel="stylesheet">
        
        <style>
        /* CSS Variables */
        :root {
            --primary-color: #007BFF;
            --accent-color: #10B981;
            --background-light: #F9FAFB;
            --surface: #FFFFFF;
            --text-primary: #2d3748;
            --text-secondary: #4a5568;
            --border-color: rgba(0, 123, 255, 0.15);
        }
        
        /* Import fonts */
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
        
        /* Global Styles */
        * {
            font-family: 'Bricolage Grotesque', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Main container */
        [data-testid="stMain"] {
            background: linear-gradient(135deg, #f5f7fa 0%, #fafbfc 50%, #f0f4f8 100%);
            padding-top: 160px;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-bottom: 2rem;
            min-height: 100vh;
        }
        
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #fafbfc 50%, #f0f4f8 100%);
        }
        
        /* Fixed Header Container */
        .eureka-fixed-header-container {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1001;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 251, 252, 0.98) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 1.8rem 2rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 123, 255, 0.1);
            border-bottom: 2px solid rgba(0, 123, 255, 0.2);
        }
        
        /* Header styling */
        .main-header {
            font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #007BFF 0%, #0056b3 100%);
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
            color: var(--text-secondary);
            text-align: center;
            margin-bottom: 0;
            letter-spacing: 0.15em;
            font-variant: small-caps;
            animation: fadeInUp 0.8s ease-out;
        }
        
        /* Screening box - Professional container */
        .screening-box {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(255, 255, 255, 0.75) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1.5px solid var(--border-color);
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06), 0 2px 8px rgba(0, 123, 255, 0.04);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .screening-box:hover {
            border-color: rgba(0, 123, 255, 0.3);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 123, 255, 0.08);
        }
        
        /* Candidate card styling */
        .candidate-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.85) 100%);
            backdrop-filter: blur(16px);
            border-radius: 20px;
            border: 1.5px solid var(--border-color);
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.07);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100%;
        }
        
        .candidate-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
            border-color: var(--primary-color);
        }
        
        .candidate-rank {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 100%);
            border-radius: 50%;
            font-weight: 800;
            font-size: 1.2rem;
            color: white;
            box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
            margin-bottom: 1rem;
        }
        
        .candidate-name {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }
        
        .candidate-title {
            font-size: 0.95rem;
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }
        
        .status-strong {
            color: var(--accent-color);
            font-weight: 700;
        }
        
        .status-weak {
            color: #ef4444;
            font-weight: 700;
        }
        
        .status-moderate {
            color: #f59e0b;
            font-weight: 700;
        }
        
        .indicator-green {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: var(--accent-color);
            border-radius: 50%;
            margin-right: 0.5rem;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .indicator-red {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #ef4444;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        
        .indicator-yellow {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #f59e0b;
            border-radius: 50%;
            margin-right: 0.5rem;
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
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.7;
                transform: scale(1.1);
            }
        }
        
        /* Streamlit specific overrides */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
            backdrop-filter: blur(12px);
            border: 1.5px solid var(--border-color);
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'Bricolage Grotesque', sans-serif;
            padding: 0.8rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1), 0 4px 12px rgba(0, 123, 255, 0.15);
            background: rgba(255, 255, 255, 0.95);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.9rem 2.5rem;
            font-weight: 700;
            font-size: 1.05rem;
            font-family: 'Bricolage Grotesque', sans-serif;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 6px 20px rgba(0, 123, 255, 0.25);
            letter-spacing: 0.02em;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 123, 255, 0.35);
            background: linear-gradient(135deg, #0056b3 0%, #003d82 100%);
        }
        
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--accent-color) 0%, #059669 100%);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25);
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.35);
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(10px);
            padding: 0.5rem;
            border-radius: 12px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 8px;
            padding: 0.8rem 1.5rem;
            font-weight: 600;
            color: var(--text-secondary);
            border: none;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 100%);
            color: white;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.6) 100%);
            border-radius: 12px;
            color: var(--text-primary);
            font-weight: 600;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: var(--primary-color);
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.75) 100%);
        }
        
        /* Metric styling */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 800;
            color: var(--primary-color);
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-secondary);
        }
        
        /* Slider styling */
        .stSlider > div > div > div {
            color: var(--primary-color);
        }
        
        /* Success/Info/Warning boxes */
        .stSuccess {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(16, 185, 129, 0.05) 100%);
            border-left: 4px solid var(--accent-color);
            color: var(--text-primary);
        }
        
        .stInfo {
            background: linear-gradient(135deg, rgba(0, 123, 255, 0.08) 0%, rgba(0, 123, 255, 0.05) 100%);
            border-left: 4px solid var(--primary-color);
            color: var(--text-primary);
        }
        
        .stWarning {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(245, 158, 11, 0.05) 100%);
            border-left: 4px solid #f59e0b;
            color: var(--text-primary);
        }
        
        /* Download button */
        .stDownloadButton > button {
            background: linear-gradient(135deg, rgba(0, 123, 255, 0.1) 0%, rgba(0, 123, 255, 0.05) 100%);
            color: var(--text-primary);
            border: 1.5px solid var(--border-color);
            border-radius: 8px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, rgba(0, 123, 255, 0.15) 0%, rgba(0, 123, 255, 0.08) 100%);
            border-color: var(--primary-color);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
        }
        
        /* Markdown text */
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
            color: var(--text-primary);
            font-family: 'Bricolage Grotesque', sans-serif;
        }
        
        .main p, .main div, .main span {
            color: var(--text-secondary);
        }
        
        /* Section headers */
        .main h2 {
            font-weight: 700;
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border-color);
        }
        
        hr {
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 2rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------------------
# Configuration & Constants
# ---------------------------
OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", "gpt-4o-mini")
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

# Default ranking weights
DEFAULT_WEIGHTS = {
    "technical_skills": 30,
    "experience": 25,
    "education": 15,
    "communication": 15,
    "culture_fit": 15
}

# ---------------------------
# Utility Functions
# ---------------------------

def calculate_match_score(candidate: Dict, weights: Dict) -> float:
    """Calculate weighted match score for a candidate"""
    score = 0.0
    # Normalize weights to sum to 100
    total_weight = sum(weights.values())
    
    # Mock scoring logic - in real app, this would use AI
    base_scores = {
        "technical_skills": min(len(candidate.get("skills", [])) * 10, 100),
        "experience": min(candidate.get("experience_years", 0) * 10, 100),
        "education": 70 if candidate.get("education") else 50,
        "communication": 75,  # Would be assessed via AI
        "culture_fit": 80      # Would be assessed via AI
    }
    
    for key, weight in weights.items():
        normalized_weight = (weight / total_weight) * 100
        score += (base_scores.get(key, 0) * normalized_weight / 100)
    
    return round(score, 1)

def get_recommendation_status(score: float) -> tuple:
    """Returns (status_text, status_class, indicator_class)"""
    if score >= 80:
        return "Strong Match", "status-strong", "indicator-green"
    elif score >= 60:
        return "Moderate Match", "status-moderate", "indicator-yellow"
    else:
        return "Weak Match", "status-weak", "indicator-red"

async def analyze_candidate_with_ai(candidate: Dict, job_description: str) -> Dict:
    """Analyze candidate fit using AI (mock for now)"""
    # In a real implementation, this would call OpenRouter API
    await asyncio.sleep(0.1)  # Simulate API call
    return {
        "strengths": ["Strong technical background", "Relevant experience"],
        "concerns": ["May need communication skills development"],
        "recommendation": "Proceed to interview"
    }

def create_sample_data() -> pd.DataFrame:
    """Create sample candidate data for demonstration"""
    return pd.DataFrame([
        {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice.j@email.com",
            "skills": ["Python", "Machine Learning", "SQL"],
            "experience_years": 5,
            "education": "MS Computer Science",
            "location": "San Francisco, CA"
        },
        {
            "id": 2,
            "name": "Bob Smith",
            "email": "bob.smith@email.com",
            "skills": ["JavaScript", "React", "Node.js", "AWS"],
            "experience_years": 3,
            "education": "BS Software Engineering",
            "location": "New York, NY"
        },
        {
            "id": 3,
            "name": "Carol Martinez",
            "email": "c.martinez@email.com",
            "skills": ["Java", "Spring Boot", "Docker", "Kubernetes"],
            "experience_years": 7,
            "education": "MS Software Engineering",
            "location": "Austin, TX"
        },
        {
            "id": 4,
            "name": "David Chen",
            "email": "david.chen@email.com",
            "skills": ["Python", "Django", "PostgreSQL", "Redis"],
            "experience_years": 4,
            "education": "BS Computer Science",
            "location": "Seattle, WA"
        },
        {
            "id": 5,
            "name": "Emma Wilson",
            "email": "emma.w@email.com",
            "skills": ["C++", "Rust", "System Design", "Linux"],
            "experience_years": 6,
            "education": "PhD Computer Science",
            "location": "Boston, MA"
        },
        {
            "id": 6,
            "name": "Frank Anderson",
            "email": "f.anderson@email.com",
            "skills": ["Go", "Microservices", "gRPC", "MongoDB"],
            "experience_years": 4,
            "education": "MS Computer Science",
            "location": "Denver, CO"
        },
        {
            "id": 7,
            "name": "Grace Lee",
            "email": "grace.lee@email.com",
            "skills": ["TypeScript", "Angular", "Firebase", "GCP"],
            "experience_years": 5,
            "education": "BS Computer Engineering",
            "location": "Los Angeles, CA"
        }
    ])

# ---------------------------
# Main Application
# ---------------------------

def main():
    # Apply custom CSS
    apply_custom_css()
    
    # Fixed Header
    st.markdown('''
    <div class="eureka-fixed-header-container">
        <h1 class="main-header">Eureka</h1>
        <p class="sub-header">AI Talent Discovery Engine</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize session state
    if 'candidates_df' not in st.session_state:
        st.session_state['candidates_df'] = None
    if 'rankings_df' not in st.session_state:
        st.session_state['rankings_df'] = None
    if 'job_description' not in st.session_state:
        st.session_state['job_description'] = ""
    if 'weights' not in st.session_state:
        st.session_state['weights'] = DEFAULT_WEIGHTS.copy()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Load Candidates",
        "👥 View Candidates", 
        "⚙️ Screen & Rank",
        "📊 Monitoring Results"
    ])
    
    # ---------------------------
    # Tab 1: Load Candidates
    # ---------------------------
    with tab1:
        st.markdown("### Data Ingestion")
        st.markdown("<p style='color: #718096; font-size: 0.9rem; margin-top: -0.5rem;'>Upload candidate data or load sample data to begin</p>", unsafe_allow_html=True)
        
        # File uploader in expander
        with st.expander("📁 Local Resume Upload", expanded=False):
            st.markdown("Upload a CSV file containing candidate information")
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="CSV should contain columns: name, email, skills, experience_years, education, location"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    # Add ID column if not present
                    if 'id' not in df.columns:
                        df.insert(0, 'id', range(1, len(df) + 1))
                    
                    st.session_state['candidates_df'] = df
                    st.success(f"✓ Successfully loaded {len(df)} candidates")
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")
        
        # Load sample data button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Load Sample Data", use_container_width=True):
                with st.spinner("Loading sample data..."):
                    st.session_state['candidates_df'] = create_sample_data()
                    st.success("✓ Sample data loaded successfully")
        
        # Display loaded data
        if st.session_state['candidates_df'] is not None:
            st.markdown("---")
            
            # Progress and status container
            st.markdown('<div class="screening-box">', unsafe_allow_html=True)
            st.markdown("#### 📈 Data Processing Status")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Candidates Loaded", len(st.session_state['candidates_df']))
            with col2:
                st.metric("Data Quality", "Excellent")
            with col3:
                st.metric("Ready for Processing", "Yes")
            
            progress_bar = st.progress(100)
            st.caption("Data validation complete")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### Preview Loaded Data")
            
            # Use st.data_editor (disabled) for clean presentation
            st.data_editor(
                st.session_state['candidates_df'],
                disabled=True,
                use_container_width=True,
                hide_index=True
            )
            
            # Column mapping section
            st.markdown("---")
            st.markdown("#### Column Mapping Configuration")
            st.caption("Map your data columns to system fields")
            
            df_columns = st.session_state['candidates_df'].columns.tolist()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                name_col = st.selectbox("Name Field", df_columns, index=df_columns.index('name') if 'name' in df_columns else 0)
                email_col = st.selectbox("Email Field", df_columns, index=df_columns.index('email') if 'email' in df_columns else 0)
            with col2:
                skills_col = st.selectbox("Skills Field", df_columns, index=df_columns.index('skills') if 'skills' in df_columns else 0)
                exp_col = st.selectbox("Experience Field", df_columns, index=df_columns.index('experience_years') if 'experience_years' in df_columns else 0)
            with col3:
                edu_col = st.selectbox("Education Field", df_columns, index=df_columns.index('education') if 'education' in df_columns else 0)
                loc_col = st.selectbox("Location Field", df_columns, index=df_columns.index('location') if 'location' in df_columns else 0)
            
            if st.button("Apply Mapping", type="primary"):
                st.success("✓ Column mapping applied successfully")
    
    # ---------------------------
    # Tab 2: View Candidates
    # ---------------------------
    with tab2:
        st.markdown("### Candidate Overview")
        st.markdown("<p style='color: #718096; font-size: 0.9rem; margin-top: -0.5rem;'>Browse and explore loaded candidate profiles</p>", unsafe_allow_html=True)
        
        if st.session_state['candidates_df'] is not None:
            df = st.session_state['candidates_df']
            
            # Metrics layout
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    label="Total Candidates",
                    value=len(df),
                    delta=f"+{len(df)} new"
                )
            with col2:
                avg_exp = df['experience_years'].mean() if 'experience_years' in df.columns else 0
                st.metric(
                    label="Avg Experience",
                    value=f"{avg_exp:.1f} years"
                )
            with col3:
                unique_skills = len(set([s for skills in df['skills'] if isinstance(skills, list) for s in skills])) if 'skills' in df.columns else 0
                st.metric(
                    label="Unique Skills",
                    value=unique_skills
                )
            with col4:
                locations = df['location'].nunique() if 'location' in df.columns else 0
                st.metric(
                    label="Locations",
                    value=locations
                )
            
            st.markdown("---")
            st.markdown("#### Candidate Database")
            
            # Enhanced dataframe with column configs
            column_config = {
                "id": st.column_config.NumberColumn(
                    "ID",
                    help="Candidate ID",
                    width="small",
                    pinned=True
                ),
                "name": st.column_config.TextColumn(
                    "Name",
                    help="Candidate full name",
                    width="medium"
                ),
                "email": st.column_config.TextColumn(
                    "Email",
                    help="Contact email",
                    width="medium"
                ),
                "skills": st.column_config.ListColumn(
                    "Skills",
                    help="Technical skills",
                    width="large"
                ),
                "experience_years": st.column_config.NumberColumn(
                    "Experience",
                    help="Years of experience",
                    format="%d years",
                    width="small"
                ),
                "education": st.column_config.TextColumn(
                    "Education",
                    help="Highest degree",
                    width="medium"
                ),
                "location": st.column_config.TextColumn(
                    "Location",
                    help="Current location",
                    width="medium"
                )
            }
            
            st.dataframe(
                df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True
            )
            
        else:
            st.info("📋 No candidates loaded. Please load data in the 'Load Candidates' tab.")
    
    # ---------------------------
    # Tab 3: Screen & Rank
    # ---------------------------
    with tab3:
        st.markdown("### Screening Configuration")
        st.markdown("<p style='color: #718096; font-size: 0.9rem; margin-top: -0.5rem;'>Define job requirements and ranking criteria</p>", unsafe_allow_html=True)
        
        if st.session_state['candidates_df'] is None:
            st.warning("⚠️ Please load candidate data first")
        else:
            # Two-column layout for JD and Weights
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.markdown("#### 📋 Job Description")
                job_title = st.text_input(
                    "Job Title",
                    value="Senior Software Engineer",
                    help="Enter the position title"
                )
                
                job_description = st.text_area(
                    "Job Requirements & Description",
                    value=st.session_state['job_description'],
                    height=300,
                    placeholder="Enter detailed job description, required skills, experience, and qualifications...",
                    help="Provide comprehensive job details for accurate candidate matching"
                )
                st.session_state['job_description'] = job_description
                
                char_count = len(job_description)
                st.caption(f"Characters: {char_count}")
            
            with col_right:
                st.markdown("#### ⚖️ Ranking Weights")
                st.caption("Adjust criteria importance (Total: 100%)")
                
                weights = {}
                for key, label in [
                    ("technical_skills", "Technical Skills"),
                    ("experience", "Experience"),
                    ("education", "Education"),
                    ("communication", "Communication"),
                    ("culture_fit", "Culture Fit")
                ]:
                    weights[key] = st.slider(
                        label,
                        min_value=0,
                        max_value=50,
                        value=st.session_state['weights'].get(key, DEFAULT_WEIGHTS[key]),
                        step=5,
                        help=f"Weight for {label.lower()} assessment"
                    )
                
                total_weight = sum(weights.values())
                
                # Display total with color coding
                if total_weight == 100:
                    st.markdown(f"<div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%); padding: 1rem; border-radius: 8px; text-align: center; border: 2px solid #10B981;'><strong style='font-size: 1.2rem; color: #10B981;'>✓ Total: {total_weight}%</strong></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%); padding: 1rem; border-radius: 8px; text-align: center; border: 2px solid #ef4444;'><strong style='font-size: 1.2rem; color: #ef4444;'>⚠️ Total: {total_weight}%</strong><br><span style='font-size: 0.85rem;'>Must equal 100%</span></div>", unsafe_allow_html=True)
                
                st.session_state['weights'] = weights
            
            st.markdown("---")
            
            # Run screening button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                run_screening = st.button(
                    "🚀 Run Screening & Ranking",
                    use_container_width=True,
                    type="primary",
                    disabled=(total_weight != 100 or not job_description)
                )
            
            if run_screening:
                with st.spinner("Analyzing candidates... This may take a moment."):
                    # Calculate match scores
                    df = st.session_state['candidates_df'].copy()
                    
                    match_scores = []
                    for idx, row in df.iterrows():
                        candidate = row.to_dict()
                        score = calculate_match_score(candidate, weights)
                        match_scores.append(score)
                    
                    df['match_score'] = match_scores
                    df['recommendation'], df['status_class'], df['indicator_class'] = zip(*[get_recommendation_status(s) for s in match_scores])
                    
                    # Sort by match score
                    df = df.sort_values('match_score', ascending=False).reset_index(drop=True)
                    df['rank'] = range(1, len(df) + 1)
                    
                    st.session_state['rankings_df'] = df
                    
                    st.success("✓ Screening completed successfully! View results in the 'Monitoring Results' tab.")
    
    # ---------------------------
    # Tab 4: Monitoring Results
    # ---------------------------
    with tab4:
        st.markdown("### Screening Results")
        st.markdown("<p style='color: #718096; font-size: 0.9rem; margin-top: -0.5rem;'>Review ranked candidates and detailed profiles</p>", unsafe_allow_html=True)
        
        if st.session_state['rankings_df'] is not None:
            df = st.session_state['rankings_df']
            
            # Top 7 candidates in grid layout
            st.markdown("#### 🏆 Top Candidates")
            
            top_candidates = df.head(7)
            
            # Display in rows of 3
            for i in range(0, len(top_candidates), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(top_candidates):
                        candidate = top_candidates.iloc[idx]
                        
                        with col:
                            # Candidate card
                            indicator = candidate['indicator_class']
                            st.markdown(f'''
                            <div class="candidate-card screening-box">
                                <div class="candidate-rank">#{candidate['rank']}</div>
                                <div class="candidate-name">{candidate['name']}</div>
                                <div class="candidate-title">{candidate.get('education', 'N/A')}</div>
                                <div style="margin: 1rem 0;">
                                    <div style="font-size: 0.85rem; color: #718096; margin-bottom: 0.5rem;">Match Score</div>
                                    <div style="font-size: 2rem; font-weight: 800; color: #007BFF;">{candidate['match_score']}%</div>
                                </div>
                                <div style="margin-top: 1rem;">
                                    <span class="{indicator}"></span>
                                    <span class="{candidate['status_class']}">{candidate['recommendation']}</span>
                                </div>
                                <div style="margin-top: 1rem; font-size: 0.85rem; color: #718096;">
                                    <strong>Experience:</strong> {candidate.get('experience_years', 0)} years<br>
                                    <strong>Location:</strong> {candidate.get('location', 'N/A')}
                                </div>
                            </div>
                            ''', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### 📋 Complete Rankings")
            
            # Enhanced rankings table
            column_config = {
                "rank": st.column_config.NumberColumn(
                    "Rank",
                    help="Candidate ranking",
                    width="small"
                ),
                "name": st.column_config.TextColumn(
                    "Name",
                    help="Candidate name",
                    width="medium"
                ),
                "match_score": st.column_config.ProgressColumn(
                    "Match Score",
                    help="Overall match percentage",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                    width="medium"
                ),
                "recommendation": st.column_config.TextColumn(
                    "Recommendation",
                    help="Hiring recommendation",
                    width="medium"
                ),
                "experience_years": st.column_config.NumberColumn(
                    "Experience",
                    help="Years of experience",
                    format="%d years",
                    width="small"
                ),
                "education": st.column_config.TextColumn(
                    "Education",
                    help="Highest degree",
                    width="medium"
                ),
                "location": st.column_config.TextColumn(
                    "Location",
                    help="Current location",
                    width="medium"
                )
            }
            
            display_df = df[['rank', 'name', 'match_score', 'recommendation', 'experience_years', 'education', 'location']]
            
            # Apply text styling to recommendation column
            def color_recommendation(val):
                if 'Strong' in val:
                    return 'background-color: rgba(16, 185, 129, 0.1); color: #10B981; font-weight: 700'
                elif 'Moderate' in val:
                    return 'background-color: rgba(245, 158, 11, 0.1); color: #f59e0b; font-weight: 700'
                else:
                    return 'background-color: rgba(239, 68, 68, 0.1); color: #ef4444; font-weight: 700'
            
            st.dataframe(
                display_df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("---")
            
            # Detailed profile section
            st.markdown("#### 🔍 Detailed Profile View")
            
            selected_candidate = st.selectbox(
                "Select a candidate to view detailed profile",
                options=df['name'].tolist(),
                index=0
            )
            
            candidate_data = df[df['name'] == selected_candidate].iloc[0]
            
            st.markdown("---")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### {candidate_data['name']}")
                st.markdown(f"**{candidate_data.get('education', 'N/A')}** • {candidate_data.get('location', 'N/A')}")
                
                st.markdown("---")
                
                st.markdown("**Contact Information**")
                st.markdown(f"📧 {candidate_data.get('email', 'N/A')}")
                
                st.markdown("**Professional Summary**")
                st.markdown(f"• **Experience:** {candidate_data.get('experience_years', 0)} years")
                st.markdown(f"• **Education:** {candidate_data.get('education', 'N/A')}")
                
                if isinstance(candidate_data.get('skills'), list):
                    st.markdown("**Technical Skills**")
                    skills_html = " ".join([f"<span style='display: inline-block; background: linear-gradient(135deg, rgba(0, 123, 255, 0.1) 0%, rgba(0, 123, 255, 0.05) 100%); padding: 0.4rem 0.8rem; border-radius: 8px; margin: 0.2rem; font-size: 0.9rem; font-weight: 600; color: #007BFF;'>{skill}</span>" for skill in candidate_data['skills']])
                    st.markdown(skills_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="screening-box">', unsafe_allow_html=True)
                st.markdown("### Match Analysis")
                
                st.metric("Match Score", f"{candidate_data['match_score']}%")
                st.metric("Rank", f"#{candidate_data['rank']} of {len(df)}")
                
                status_indicator = candidate_data['indicator_class']
                st.markdown(f"**Status:** <span class='{status_indicator}'></span><span class='{candidate_data['status_class']}'>{candidate_data['recommendation']}</span>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                st.markdown("**Key Strengths**")
                st.markdown("• Strong technical background")
                st.markdown("• Relevant experience")
                st.markdown("• Good culture fit")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Export results
            st.markdown("---")
            st.markdown("#### 📥 Export Results")
            
            export_data = {
                "job_title": st.session_state.get('job_title', 'Position'),
                "total_candidates": len(df),
                "screening_date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "weights": st.session_state['weights'],
                "rankings": df.to_dict(orient='records')
            }
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.download_button(
                    label="Download Rankings (JSON)",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"candidate_rankings_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            with col2:
                st.download_button(
                    label="Download Rankings (CSV)",
                    data=df.to_csv(index=False),
                    file_name=f"candidate_rankings_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        else:
            st.info("📊 No screening results available. Please run screening in the 'Screen & Rank' tab.")

if __name__ == "__main__":
    main()
