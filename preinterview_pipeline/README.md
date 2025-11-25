# Preinterview Pipeline

A comprehensive backend service for resume ingestion, candidate enrichment, skill gap analysis, and interview plan generation.

## Features

### 1. Resume Ingestion & Parsing
- **PDF/DOCX Support**: Parse resumes from PDF and DOCX files using pdfminer and python-docx
- **Custom Extraction**: Uses regex-based extraction for email, phone, location, skills, education, and experience
- **Normalized Schema**: Converts unstructured resume data into normalized `CandidateProfile` objects
- **Confidence Scoring**: Returns confidence metrics and parsing warnings for data quality assessment
- **Deduplication**: Computes SHA256 hash of CV files to detect duplicates

### 2. Profile Enrichment
- **LinkedIn Integration**: Enrich profiles with public LinkedIn data
- **GitHub Integration**: Extract technical skills and activity from GitHub profiles
- **Rate Limiting**: Implements exponential backoff and rate limiting for API calls
- **Async Operations**: Uses async/await for concurrent enrichment operations
- **Provenance Tracking**: Logs enrichment operations with timestamps and confidence scores

### 3. Skill Gap Analysis
- **Multi-Level Assessment**: Compares candidate skills against job requirements with proficiency levels
- **Gap Classification**: Categorizes gaps as critical, significant, minor, or no gap
- **Readiness Levels**: Classifies candidates as ready, trainable, consider, or not suitable
- **Strength Identification**: Highlights candidate strengths aligned with nice-to-have requirements
- **Weighted Scoring**: Factors in requirement importance and candidate experience

### 4. Interview Plan Generation
- **Adaptive Plans**: Generates interview plans tailored to candidate level and gap analysis
- **Multiple Formats**: Supports phone screen, technical, full-loop, and executive interview formats
- **Competency Focus**: Customizes competency assessment based on gaps and role needs
- **Question Generation**: Provides interview questions with difficulty levels, follow-ups, and evaluation criteria
- **Risk Assessment**: Identifies potential risk indicators to monitor during interviews

### 5. REST API Endpoints
All endpoints include validation, error handling, and comprehensive documentation.

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status.

### Resume Parsing
```
POST /resume/parse
```
Parse a resume file (PDF/DOCX) into a normalized candidate profile.

**Request:**
- File upload (multipart/form-data)
- Optional: candidate_name, candidate_email

**Response:**
```json
{
  "candidate_profile": {...},
  "parsing_confidence": 0.95,
  "parsing_warnings": []
}
```

### Profile Enrichment
```
POST /enrichment/enrich
```
Enrich candidate profile with LinkedIn and/or GitHub data.

**Request:**
```json
{
  "candidate_id": "C001",
  "sources": ["linkedin", "github"],
  "update_existing": false
}
```

**Response:**
```json
{
  "candidate_id": "C001",
  "enriched_profile": {...},
  "enrichment_results": {...}
}
```

### Gap Analysis
```
POST /gap-analysis/analyze
```
Analyze skill gaps between candidate and job requirements.

**Request:**
```json
{
  "candidate_id": "C001",
  "job_specification": {...}
}
```

**Response:**
```json
{
  "candidate_id": "C001",
  "job_id": "J001",
  "critical_gaps": [...],
  "significant_gaps": [...],
  "minor_gaps": [...],
  "strengths": [...],
  "overall_fit_score": 78.5,
  "readiness_level": "trainable",
  "summary": "..."
}
```

### Interview Plan Generation
```
POST /interview-plan/generate
```
Generate a structured interview plan based on gap analysis.

**Request:**
```json
{
  "candidate_id": "C001",
  "gap_analysis": {...},
  "interview_format": "full_loop"
}
```

**Response:**
```json
{
  "plan_id": "IP-xxx",
  "candidate_id": "C001",
  "job_id": "J001",
  "interview_focus": "...",
  "interview_duration_minutes": 180,
  "competency_focus": [...],
  "questions": [...],
  "critical_gap_exploration": "...",
  "strength_validation": "...",
  "risk_indicators": [...]
}
```

## Data Models

### CandidateProfile
Normalized representation of a candidate including:
- Basic info (name, email, phone, location)
- Professional experience (companies, titles, duration)
- Skills with proficiency levels
- Education background
- Social profiles (LinkedIn, GitHub)
- Raw CV content (encrypted in production)
- Enrichment metadata

### JobSpecification
Job requirements including:
- Job title and description
- Required skills with proficiency levels
- Minimum experience years
- Preferred and nice-to-have skills
- Importance weights for each requirement

### GapAnalysisResult
Gap analysis output with:
- Critical, significant, and minor gaps
- Candidate strengths
- Overall fit score (0-100)
- Readiness level classification
- Human-readable summary

### InterviewPlan
Structured interview plan with:
- Interview format and duration
- Competency focus areas
- Interview questions with follow-ups
- Evaluation criteria
- Guidance for critical gaps and strengths
- Risk indicators to monitor

## Running the API

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn preinterview_pipeline.api:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Run production server
uvicorn preinterview_pipeline.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```bash
docker build -t preinterview-pipeline .
docker run -p 8000:8000 preinterview-pipeline
```

## Testing

Run comprehensive test suite:
```bash
# Run all tests
pytest preinterview_pipeline/test_*.py -v

# Run specific test file
pytest preinterview_pipeline/test_gap_analysis.py -v

# Run with coverage
pytest preinterview_pipeline/test_*.py --cov=preinterview_pipeline
```

Test coverage includes:
- Resume parsing and extraction
- Gap analysis and readiness classification
- Interview plan generation
- Enrichment operations
- API endpoint validation
- Error handling

## Architecture

### Modular Design
- `models.py`: Pydantic data models and schemas
- `resume_parser.py`: Resume parsing and extraction logic
- `enrichment.py`: LinkedIn/GitHub enrichment modules with rate limiting
- `gap_analysis.py`: Skill gap analysis engine
- `interview_plan.py`: Interview plan generation
- `api.py`: FastAPI REST API endpoints

### Key Design Patterns
- **Type Safety**: Full type hints and Pydantic validation
- **Async Operations**: Async/await for non-blocking I/O
- **Rate Limiting**: Prevents API throttling and respects service limits
- **Provenance Tracking**: Audit trail for all enrichment operations
- **Confidence Scoring**: Data quality indicators for all extracted information

## Configuration

Environment variables:
- `GITHUB_TOKEN`: GitHub API token for higher rate limits
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

## Safety & Compliance

### Bias Mitigation
- No demographic inference from CV
- Fair competency assessment based on skills and experience
- Readiness levels avoid age/background bias

### Data Security
- CV content stored with field-level encryption (in production)
- No PII exposed in API responses (user control)
- Audit trail for all data access

### API Safety
- Request validation on all endpoints
- Rate limiting to prevent abuse
- CORS configuration for cross-origin access
- Comprehensive error handling and logging

## Performance

### Optimization
- Async enrichment for concurrent API calls
- Rate limiting prevents throttling
- Efficient regex-based parsing
- Caching support for repeated queries

### Scalability
- Stateless API design for horizontal scaling
- PostgreSQL backend for persistence (in production)
- Background task support for long-running operations

## Future Enhancements

- PostgreSQL integration for persistence
- Background job queuing (Celery/RQ)
- LLM-powered resume understanding
- Advanced interview question generation using GPT
- Candidate-job matching ML model
- Interview performance prediction
- Salary negotiation guidance
