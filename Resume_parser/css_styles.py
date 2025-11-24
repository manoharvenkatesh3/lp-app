"""Custom CSS styles and fonts for the Eureka - AI Talent Discovery Engine."""


def apply_custom_css() -> str:
    """Returns Eureka enterprise CSS string."""
    return """
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&display=swap" rel="stylesheet">
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
    
    :root {
        --primary-color: #007BFF;
        --accent-color: #10B981;
        --background-light: #F9FAFB;
        --surface: #FFFFFF;
        --text-primary: #1F2937;
        --text-secondary: #6B7280;
        --border-subtle: rgba(0, 123, 255, 0.12);
        --shadow-lifted: 0 6px 24px rgba(0, 0, 0, 0.08);
        --shadow-hover: 0 12px 36px rgba(0, 0, 0, 0.12);
    }
    
    * {
        font-family: 'Bricolage Grotesque', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #dbeafe 100%);
    }
    
    [data-testid="stMain"] {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #dbeafe 100%);
        padding-top: 160px !important;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 2rem;
    }
    
    .eureka-fixed-header-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 10000;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(224, 242, 254, 0.98) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 1.2rem 2rem 0.8rem 2rem;
        box-shadow: 0 4px 20px rgba(0, 123, 255, 0.12);
        border-bottom: 2px solid rgba(0, 123, 255, 0.15);
    }
    
    .eureka-main-header {
        font-family: 'Bricolage Grotesque', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #007BFF 0%, #0056b3 50%, #004085 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.4rem;
        letter-spacing: 0.08em;
    }
    
    .eureka-sub-header {
        font-family: 'Bricolage Grotesque', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 0;
        letter-spacing: 0.05em;
    }
    
    .screening-box {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.8) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1.5px solid var(--border-subtle);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-lifted);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .screening-box:hover {
        border-color: rgba(0, 123, 255, 0.25);
        box-shadow: var(--shadow-hover);
        transform: translateY(-4px);
    }
    
    .candidate-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(240, 249, 255, 0.9) 100%);
        backdrop-filter: blur(14px);
        border-radius: 20px;
        border: 1.5px solid rgba(0, 123, 255, 0.15);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 28px rgba(0, 123, 255, 0.08);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .candidate-card:hover {
        border-color: rgba(0, 123, 255, 0.35);
        box-shadow: 0 16px 40px rgba(0, 123, 255, 0.15);
        transform: translateY(-6px) scale(1.01);
    }
    
    .recommendation-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    
    .recommendation-strong {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.08) 100%);
        color: #059669;
        border: 1.5px solid rgba(16, 185, 129, 0.3);
    }
    
    .recommendation-balanced {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(249, 115, 22, 0.08) 100%);
        color: #c2410c;
        border: 1.5px solid rgba(249, 115, 22, 0.3);
    }
    
    .recommendation-watch {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.15) 0%, rgba(244, 63, 94, 0.08) 100%);
        color: #be123c;
        border: 1.5px solid rgba(244, 63, 94, 0.3);
    }
    
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
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.75) 100%);
        backdrop-filter: blur(12px);
        border: 1.5px solid rgba(0, 123, 255, 0.2);
        border-radius: 10px;
        color: var(--text-primary);
        font-family: 'Bricolage Grotesque', sans-serif;
        padding: 0.8rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1), 0 4px 12px rgba(0, 123, 255, 0.15);
        background: rgba(255, 255, 255, 0.98);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.85rem 2.2rem;
        font-weight: 700;
        font-size: 1rem;
        font-family: 'Bricolage Grotesque', sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(0, 123, 255, 0.25);
        letter-spacing: 0.02em;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 123, 255, 0.35);
        background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(240, 249, 255, 0.98) 100%);
        backdrop-filter: blur(20px);
        border-right: 2px solid rgba(0, 123, 255, 0.12);
    }
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 255, 255, 0.65) 100%);
        border-radius: 10px;
        color: var(--text-primary);
        font-weight: 600;
        border: 1px solid rgba(0, 123, 255, 0.15);
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(0, 123, 255, 0.3);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.75) 100%);
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
    }
    
    .stMetric {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 249, 255, 0.7) 100%);
        backdrop-filter: blur(12px);
        border-radius: 14px;
        border: 1.5px solid rgba(0, 123, 255, 0.15);
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(0, 123, 255, 0.08);
    }
    
    .stMetric label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--primary-color);
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.6) 100%);
        border-radius: 10px 10px 0 0;
        color: var(--text-secondary);
        font-weight: 600;
        border: 1.5px solid rgba(0, 123, 255, 0.1);
        border-bottom: none;
        padding: 0.8rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.75) 100%);
        border-color: rgba(0, 123, 255, 0.25);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 123, 255, 0.12) 0%, rgba(0, 123, 255, 0.05) 100%);
        border-color: var(--primary-color);
        color: var(--primary-color);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(0, 123, 255, 0.1) 0%, rgba(0, 123, 255, 0.05) 100%);
        color: var(--primary-color);
        border: 1.5px solid rgba(0, 123, 255, 0.3);
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, rgba(0, 123, 255, 0.15) 0%, rgba(0, 123, 255, 0.08) 100%);
        border-color: rgba(0, 123, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-family: 'Bricolage Grotesque', sans-serif;
    }
    
    p, div, span {
        color: var(--text-secondary);
    }
    
    hr {
        border: none;
        border-top: 1px solid rgba(0, 123, 255, 0.12);
        margin: 2rem 0;
    }
    </style>
    """
