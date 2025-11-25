# Multi-Application Platform

This repository contains multiple applications:

## 1. Loyalty Program (Legacy)
Original loyalty program evaluator - see `streamlit_app.py`

## 2. Eureka AI Talent Discovery Engine
Resume parser and candidate screening - see `Resume_parser/` folder

## 3. LLM Council
Multi-model decision making system - see `llm_council/` folder

## 4. **Recruiter Dashboard & ATS Integration** (NEW)
Comprehensive recruiter dashboard with real-time monitoring, RBAC, and ATS integration.

### Features
- **Dashboard**: Real-time interview metrics and statistics
- **Live Monitoring**: WebSocket-based interview monitoring with AI whisper suggestions
- **Candidate History**: Timeline visualizations and performance tracking
- **Authentication**: JWT-based auth with role-based access control (Admin/Hiring Manager/Recruiter)
- **ATS Integration**: REST API for candidate sync, scorecard export, and feedback
- **Bias Detection**: Automated bias checking and inclusive language suggestions
- **Audit Logging**: Complete audit trail for compliance

### Quick Start

**Backend:**
```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost/recruiter_db"
export JWT_SECRET_KEY="your-secret-key"
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Docker:**
```bash
docker-compose up -d
```

### Documentation
- [Complete Dashboard Documentation](DASHBOARD_README.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Sample ATS Integration Script](scripts/ats_integration_sample.py)

### API Endpoints
- Dashboard: `http://localhost:3000`
- Backend API: `http://localhost:8000/api`
- API Docs: `http://localhost:8000/api/docs`

---

## Project Structure

```
/
├── streamlit_app.py          # Legacy loyalty program
├── Resume_parser/            # Talent discovery engine
├── llm_council/              # LLM council system
├── backend/                  # NEW: Recruiter dashboard API
│   ├── main.py
│   ├── models.py
│   ├── routers/
│   ├── middleware/
│   └── schemas/
├── frontend/                 # NEW: React dashboard UI
│   └── src/
└── scripts/                  # NEW: ATS integration samples
```
