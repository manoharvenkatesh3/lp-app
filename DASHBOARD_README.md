# Recruiter Dashboard & ATS Integration

A comprehensive recruiter dashboard with real-time interview monitoring, RBAC authentication, ATS integration, and bias-filtered audit logging.

## Features

### Dashboard & Interview Management
- **Dashboard Overview**: Real-time statistics and metrics for interview pipeline
- **Scheduling**: Interview scheduling with calendar integration
- **Pre-Interview Prep**: Candidate research and preparation tools
- **Live Monitoring**: Real-time interview monitoring with WebSocket feed
  - Live transcript streaming
  - AI-powered whisper suggestions overlay
  - Interview controls and status updates
- **Post-Interview Analytics**: Performance metrics and trend analysis
- **Candidate History**: Complete timeline visualization with scorecard tracking

### Authentication & Authorization
- **JWT-based authentication** with secure token storage
- **Role-based access control (RBAC)**:
  - **Admin**: Full system access, user management, audit logs
  - **Hiring Manager**: Team interviews, scorecards, analytics
  - **Recruiter**: Own interviews, monitoring, candidate management
- **Frontend role detection** for conditional UI rendering
- **Secure password hashing** with bcrypt

### ATS Integration
- **REST API endpoints** for external ATS systems:
  - `POST /api/ats/candidates/sync`: Push candidates to platform
  - `GET /api/ats/candidates`: Pull candidate data (incremental sync)
  - `GET /api/ats/scorecards/export`: Export interview scorecards
  - `POST /api/ats/feedback/sync`: Sync additional feedback
- **API key authentication** with secure storage
- **Rate limiting**: 1000 requests/hour per integration
- **OpenAPI documentation**: `/api/docs` and `/api/redoc`

### Bias Detection & Safety
- **Automated bias checking** on all scorecards and feedback
- **Bias indicators**: Age, gender, race, disability, appearance, family status
- **Inclusive language suggestions** with automatic sanitization
- **Safety constraints**:
  - Extreme score validation
  - Justification requirements for low scores
  - Recommendation consistency checks

### Audit & Compliance
- **Complete audit logging** for all actions
- **Logged information**:
  - User actions and timestamps
  - Resource access patterns
  - IP addresses and user agents
  - Bias check results
  - Safety flag violations
- **Audit log API** for compliance reporting

## Architecture

### Backend (FastAPI)
```
backend/
├── main.py              # FastAPI application
├── models.py            # SQLAlchemy database models
├── database.py          # Database configuration
├── routers/
│   ├── auth.py         # Authentication endpoints
│   ├── recruiter.py    # Recruiter dashboard endpoints
│   └── ats.py          # ATS integration endpoints
├── middleware/
│   ├── rbac.py         # Role-based access control
│   ├── audit.py        # Audit logging
│   ├── bias_filter.py  # Bias detection & filtering
│   └── rate_limit.py   # API rate limiting
├── schemas/
│   ├── auth.py         # Auth schemas
│   ├── candidate.py    # Candidate schemas
│   ├── interview.py    # Interview schemas
│   └── scorecard.py    # Scorecard schemas
└── utils/
    ├── jwt.py          # JWT token utilities
    └── websocket.py    # WebSocket manager
```

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── App.tsx                    # Main application
│   ├── pages/
│   │   ├── Dashboard.tsx         # Dashboard overview
│   │   ├── LiveMonitoring.tsx    # Real-time monitoring
│   │   └── CandidateHistory.tsx  # History viewer
│   ├── components/
│   │   ├── auth/
│   │   │   └── Login.tsx         # Login form
│   │   ├── dashboard/
│   │   │   ├── ScorecardViewer.tsx    # Scorecard display
│   │   │   ├── TimelineChart.tsx      # Timeline visualization
│   │   │   └── WhisperOverlay.tsx     # AI suggestions overlay
│   │   └── layout/
│   │       ├── Header.tsx        # App header
│   │       └── Sidebar.tsx       # Navigation sidebar
│   ├── hooks/
│   │   ├── useAuth.ts            # Authentication hook
│   │   └── useWebSocket.ts       # WebSocket hook
│   ├── services/
│   │   ├── api.ts                # API client
│   │   └── auth.ts               # Auth service
│   ├── utils/
│   │   └── tokenStorage.ts       # Secure token storage
│   └── types/
│       └── index.ts              # TypeScript types
└── package.json
```

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for production rate limiting)

### Backend Setup

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment variables**:
```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/recruiter_db"
export JWT_SECRET_KEY="your-secret-key-change-in-production"
```

3. **Initialize database**:
```bash
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

4. **Run the server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Configure environment**:
```bash
cp .env.example .env
```

3. **Run development server**:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## API Documentation

### Authentication

**Register User**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "recruiter@company.com",
  "username": "recruiter1",
  "password": "securepass123",
  "role": "recruiter"
}
```

**Login**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "recruiter@company.com",
  "password": "securepass123"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Get Current User**
```bash
GET /api/auth/me
Authorization: Bearer <token>
```

### Recruiter Dashboard

**Get Dashboard Stats**
```bash
GET /api/recruiter/dashboard/stats
Authorization: Bearer <token>
```

**List Interviews**
```bash
GET /api/recruiter/interviews?page=1&page_size=20&status=scheduled
Authorization: Bearer <token>
```

**Create Interview**
```bash
POST /api/recruiter/interviews
Authorization: Bearer <token>
Content-Type: application/json

{
  "candidate_id": 123,
  "position": "Senior Software Engineer",
  "scheduled_at": "2024-02-01T10:00:00Z",
  "meeting_link": "https://zoom.us/j/123456",
  "prep_data": {"resume_reviewed": true}
}
```

**Create Scorecard** (with bias checking)
```bash
POST /api/recruiter/scorecards
Authorization: Bearer <token>
Content-Type: application/json

{
  "interview_id": 456,
  "candidate_id": 123,
  "technical_score": 85,
  "communication_score": 90,
  "cultural_fit_score": 88,
  "overall_score": 87.5,
  "strengths": ["Strong problem-solving", "Excellent communication"],
  "weaknesses": ["Limited cloud experience"],
  "recommendation": "recommend",
  "detailed_feedback": "Excellent candidate with strong technical skills..."
}
```

**WebSocket Connection** (Live Monitoring)
```javascript
const ws = new WebSocket('ws://localhost:8000/api/recruiter/ws/interview/456');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  // Handle whisper, transcript, or status updates
};
```

### ATS Integration

**Register ATS Integration**
```bash
POST /api/ats/integrations/register
Content-Type: application/json

{
  "name": "Greenhouse",
  "webhook_url": "https://yourcompany.com/webhook"
}

Response:
{
  "integration_id": 1,
  "name": "Greenhouse",
  "api_key": "ats_xxx...",
  "message": "Store this API key securely. It cannot be retrieved again."
}
```

**Sync Candidate** (Push to Platform)
```bash
POST /api/ats/candidates/sync
X-API-Key: ats_xxx...
Content-Type: application/json

{
  "external_id": "GH-12345",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "skills": ["Python", "React"],
  "experience_years": 5
}
```

**Pull Candidates** (Incremental Sync)
```bash
GET /api/ats/candidates?updated_since=2024-01-01T00:00:00Z&page=1&page_size=50
X-API-Key: ats_xxx...
```

**Export Scorecards**
```bash
GET /api/ats/scorecards/export?from_date=2024-01-01T00:00:00Z
X-API-Key: ats_xxx...
```

## Sample Integration Script

A complete Python example demonstrating ATS integration:

```bash
cd scripts
export ATS_API_KEY="your-api-key"
python ats_integration_sample.py
```

The script demonstrates:
- Pushing candidates to the platform
- Pulling candidate data
- Exporting scorecards
- Syncing feedback

## Security Best Practices

1. **JWT Tokens**: Store in `localStorage` with automatic cleanup
2. **API Keys**: Never commit to version control, use environment variables
3. **Rate Limiting**: 1000 requests/hour for ATS endpoints
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure allowed origins in production
6. **Database**: Use connection pooling and parameterized queries
7. **Passwords**: Bcrypt hashing with salt

## Bias Detection Examples

**Flagged Language**:
- ❌ "young and energetic candidate"
- ✅ "early-career candidate with enthusiasm"

- ❌ "good culture fit for the guys on the team"
- ✅ "strong team alignment and collaboration skills"

**Automatic Sanitization**:
- Input: "Young developer with fresh ideas"
- Output: "Early-career developer with innovative ideas"

## Accessibility Features

- **Keyboard navigation**: Full support for tab navigation
- **ARIA labels**: Proper labeling for screen readers
- **Color contrast**: WCAG AA compliance
- **Focus indicators**: Clear visual focus states
- **Responsive design**: Mobile-friendly layouts

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### E2E Tests
```bash
npm run test:e2e
```

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment

**Backend**:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend**:
```bash
npm run build
# Serve the dist/ folder with nginx or your preferred web server
```

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Create an issue on GitHub
- Email: support@yourcompany.com
- Documentation: https://docs.yourcompany.com
