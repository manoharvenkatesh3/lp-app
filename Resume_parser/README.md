# Eureka - AI Talent Discovery Engine

A world-class enterprise UI for intelligent resume parsing, candidate screening, and talent analytics.

## 🎯 Overview

Eureka is a polished Streamlit application that transforms raw candidate data into actionable recruiting intelligence. With a glassmorphism design aesthetic and data-centric usability, Eureka empowers enterprise recruiting teams to discover, screen, and rank top talent efficiently.

## 📁 Project Structure

```
Resume_parser/
├── __init__.py           # Package initialization
├── streamlit_app.py      # Main Streamlit application (4 tabs)
├── constants.py          # Core constants, default data, and configuration
├── css_styles.py         # Custom CSS variables and styling
├── utils.py              # Utility functions for data processing and scoring
└── README.md             # This file
```

## 🚀 Features

### Tab 1: Load Candidates
- **Local Resume Upload:** Upload CSV, Excel, or JSON files via file uploader (wrapped in expander)
- **Google Sheets Integration:** Fetch candidate data directly from Google Sheets with URL/ID input
- **Column Mapping:** Intuitive selectboxes for mapping uploaded columns to Eureka standard fields
- **Processing Status:** Visual progress indicators and status messages

### Tab 2: View Candidates
- **Metrics Dashboard:** Clean `st.metric` cards showing Total Candidates, Avg Experience, Immediate Ready, Remote Ready
- **Enhanced Dataframe:** `st.data_editor` with custom column configs:
  - Pinned `id` column
  - `ListColumn` for skills with clean display
  - `NumberColumn` for experience years
- **Full data visibility** with disabled editing for read-only viewing

### Tab 3: Screen & Rank
- **Structured Layout:** Side-by-side job description and ranking weights using `st.columns([2, 1])`
- **Job Configuration:** Job title, full description, work model, and minimum experience inputs
- **Weight Sliders:** Interactive sliders for Skills Alignment, Experience Fit, and Culture Impact
- **Validation:** Real-time validation ensuring weights sum to 100%
- **Scoring Engine:** One-click screening with AI-powered candidate ranking

### Tab 4: Monitoring Results
- **Top 7 Grid Layout:** Elegant candidate cards displayed in 2-3 columns using nested `st.columns`
- **Recommendation Badges:** Colored indicators (Strong/Balanced/Watch) with styled badges
- **Rankings Table:** Enhanced dataframe with:
  - `ProgressColumn` for Match Score
  - Custom formatting for Recommendation status
  - Pinned ID column
- **Detailed Profile Viewer:** Expandable detailed view for selected candidates
- **Export:** Download full results as JSON

## 🎨 Design System

### CSS Variables
- `--primary-color`: #007BFF (enterprise blue)
- `--accent-color`: #10B981 (success green)
- `--background-light`: #F9FAFB (subtle gradient base)
- `--surface`: #FFFFFF (clean white surfaces)

### Typography
- **Font Family:** Bricolage Grotesque (consistent across all components)
- **Icons:** Material Symbols Outlined

### Styling Classes
- `.screening-box`: Glassmorphism container with lifted shadow effect
- `.candidate-card`: Card component for top candidate display
- `.recommendation-badge`: Status indicator with color variants
- `.eureka-fixed-header-container`: Fixed header with blur and gradient

## 📊 Data Flow

1. **Ingestion:** Raw data loaded from local files or Google Sheets
2. **Normalization:** Column mapping applies standard Eureka schema
3. **Scoring:** AI-powered scoring based on job requirements and configurable weights
4. **Presentation:** Ranked candidates displayed in elegant grid and table views
5. **Export:** Results available as structured JSON

## 🛠️ Technical Stack

- **Frontend:** Streamlit 1.28.0+
- **Data Processing:** pandas 2.0.0+
- **HTTP Requests:** httpx 0.24.0+
- **Visualization:** Custom CSS with Material Design icons

## 📦 Installation & Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

## 🔧 Configuration

Default candidates and screening configuration can be customized in `constants.py`:
- `DEFAULT_CANDIDATES`: Seed candidate dataset
- `DEFAULT_SCREEN_CONFIG`: Default job description and weights
- `REQUIRED_FIELDS`: Schema for candidate data

## 🎯 Key Utilities

### `utils.py`
- `parse_uploaded_file()`: Parse CSV, Excel, or JSON uploads
- `fetch_google_sheet()`: Fetch data from Google Sheets
- `apply_column_mapping()`: Map raw columns to Eureka schema
- `score_candidates()`: Core AI scoring engine
- `compute_summary_metrics()`: Calculate dashboard metrics

### `css_styles.py`
- `apply_custom_css()`: Returns complete Eureka CSS styling

## 🌟 Design Principles

1. **Enterprise-Ready:** Polished UI suitable for production recruiting environments
2. **Data-Centric:** Enhanced dataframes, metrics, and visualizations prioritize data clarity
3. **Modular:** Clean separation of concerns (CSS, utilities, constants, app)
4. **Accessible:** Clear labels, helpful captions, and intuitive navigation
5. **Consistent:** Unified color palette, typography, and component styling

## 📈 Future Enhancements

- AI-powered resume parsing from PDF/DOCX files
- Advanced filtering and search within candidate tables
- Integration with ATS systems (Greenhouse, Lever, etc.)
- Real-time collaboration features for recruiting teams
- Analytics dashboard with historical hiring trends

---

**Built with ❤️ using Streamlit • Designed for Enterprise Recruiting Excellence**
