# API Documentation

Complete API reference for the Recruiter Dashboard and ATS Integration platform.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

For ATS endpoints, use API key authentication:

```
X-API-Key: <ats_api_key>
```

## Endpoints

### Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "role": "recruiter"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "role": "recruiter",
  "is_active": true
}
```

#### POST /auth/login
Authenticate and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "role": "recruiter",
  "is_active": true
}
```

#### GET /auth/role
Detect current user's role and permissions.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "role": "recruiter",
  "permissions": [
    "view_own_interviews",
    "create_scorecards",
    "schedule_interviews",
    "monitor_interviews"
  ]
}
```

---

### Recruiter Dashboard Endpoints

#### GET /recruiter/dashboard/stats
Get dashboard statistics.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "total_interviews": 45,
  "scheduled": 12,
  "in_progress": 2,
  "completed": 30,
  "today": 3
}
```

#### GET /recruiter/interviews
List interviews for current recruiter.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 20): Items per page
- `status` (string, optional): Filter by status (scheduled, in_progress, completed, cancelled)

**Response:** `200 OK`
```json
{
  "total": 45,
  "interviews": [
    {
      "id": 123,
      "candidate_id": 456,
      "recruiter_id": 1,
      "position": "Senior Software Engineer",
      "scheduled_at": "2024-02-01T10:00:00Z",
      "status": "scheduled",
      "meeting_link": "https://zoom.us/j/123456",
      "created_at": "2024-01-15T09:00:00Z",
      "updated_at": "2024-01-15T09:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20
}
```

#### POST /recruiter/interviews
Schedule a new interview.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "candidate_id": 456,
  "position": "Senior Software Engineer",
  "scheduled_at": "2024-02-01T10:00:00Z",
  "meeting_link": "https://zoom.us/j/123456",
  "notes": "Focus on system design",
  "prep_data": {
    "resume_reviewed": true,
    "linkedin_checked": true
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 123,
  "candidate_id": 456,
  "recruiter_id": 1,
  "position": "Senior Software Engineer",
  "scheduled_at": "2024-02-01T10:00:00Z",
  "status": "scheduled",
  "meeting_link": "https://zoom.us/j/123456",
  "notes": "Focus on system design",
  "prep_data": {
    "resume_reviewed": true,
    "linkedin_checked": true
  },
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T09:00:00Z"
}
```

#### GET /recruiter/interviews/{interview_id}
Get interview details.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 123,
  "candidate_id": 456,
  "recruiter_id": 1,
  "position": "Senior Software Engineer",
  "scheduled_at": "2024-02-01T10:00:00Z",
  "started_at": "2024-02-01T10:05:00Z",
  "ended_at": null,
  "status": "in_progress",
  "meeting_link": "https://zoom.us/j/123456",
  "notes": "Focus on system design",
  "prep_data": {
    "resume_reviewed": true
  },
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-02-01T10:05:00Z"
}
```

#### PATCH /recruiter/interviews/{interview_id}
Update interview details.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "completed",
  "ended_at": "2024-02-01T11:00:00Z",
  "notes": "Excellent candidate"
}
```

**Response:** `200 OK`
```json
{
  "id": 123,
  "status": "completed",
  "ended_at": "2024-02-01T11:00:00Z",
  "notes": "Excellent candidate",
  ...
}
```

#### POST /recruiter/scorecards
Create an interview scorecard (with bias checking).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "interview_id": 123,
  "candidate_id": 456,
  "technical_score": 85,
  "communication_score": 90,
  "cultural_fit_score": 88,
  "overall_score": 87.5,
  "strengths": [
    "Strong problem-solving skills",
    "Excellent communication"
  ],
  "weaknesses": [
    "Limited cloud experience"
  ],
  "recommendation": "recommend",
  "detailed_feedback": "The candidate demonstrated excellent technical skills and communication abilities throughout the interview."
}
```

**Response:** `201 Created`
```json
{
  "id": 789,
  "interview_id": 123,
  "candidate_id": 456,
  "technical_score": 85,
  "communication_score": 90,
  "cultural_fit_score": 88,
  "overall_score": 87.5,
  "strengths": ["Strong problem-solving skills", "Excellent communication"],
  "weaknesses": ["Limited cloud experience"],
  "recommendation": "recommend",
  "detailed_feedback": "The candidate demonstrated excellent technical skills...",
  "bias_check_passed": true,
  "bias_flags": null,
  "created_at": "2024-02-01T11:30:00Z",
  "updated_at": "2024-02-01T11:30:00Z"
}
```

#### GET /recruiter/candidates
List candidates.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 20): Items per page
- `search` (string, optional): Search by name or email

**Response:** `200 OK`
```json
{
  "total": 150,
  "candidates": [
    {
      "id": 456,
      "external_id": "ATS-12345",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone": "+1234567890",
      "skills": ["Python", "React", "AWS"],
      "experience_years": 5.0,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-10T08:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20
}
```

#### GET /recruiter/candidates/{candidate_id}/history
Get candidate interview history with timeline.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "candidate": {
    "id": 456,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    ...
  },
  "timeline": [
    {
      "type": "interview",
      "date": "2024-01-15T10:00:00Z",
      "position": "Software Engineer",
      "status": "completed"
    },
    {
      "type": "scorecard",
      "date": "2024-01-15T11:30:00Z",
      "overall_score": 87.5,
      "recommendation": "recommend"
    }
  ],
  "total_interviews": 3,
  "average_score": 85.0
}
```

#### WebSocket /recruiter/ws/interview/{interview_id}
Connect to live interview monitoring.

**Protocol:** WebSocket

**Connection:** `ws://localhost:8000/api/recruiter/ws/interview/{interview_id}`

**Message Types:**

**Whisper Suggestion:**
```json
{
  "type": "whisper",
  "suggestion": "Ask about their experience with microservices",
  "context": "Candidate mentioned distributed systems",
  "timestamp": "2024-02-01T10:15:00Z"
}
```

**Transcript Update:**
```json
{
  "type": "transcript",
  "speaker": "Candidate",
  "text": "I have 5 years of experience with Python...",
  "timestamp": "2024-02-01T10:15:00Z"
}
```

**Status Update:**
```json
{
  "type": "status",
  "status": "in_progress",
  "details": {
    "duration_minutes": 15
  },
  "timestamp": "2024-02-01T10:15:00Z"
}
```

---

### ATS Integration Endpoints

#### POST /ats/integrations/register
Register a new ATS integration and receive API key.

**Request Body:**
```json
{
  "name": "Greenhouse",
  "webhook_url": "https://yourcompany.com/webhook"
}
```

**Response:** `201 Created`
```json
{
  "integration_id": 1,
  "name": "Greenhouse",
  "api_key": "ats_xxx...",
  "message": "Store this API key securely. It cannot be retrieved again."
}
```

#### POST /ats/candidates/sync
Sync a candidate from ATS to platform.

**Headers:** `X-API-Key: <ats_api_key>`

**Rate Limit:** 1000 requests/hour

**Request Body:**
```json
{
  "external_id": "GH-12345",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "phone": "+1234567890",
  "resume_url": "https://example.com/resume.pdf",
  "linkedin_url": "https://linkedin.com/in/janesmith",
  "skills": ["Python", "Machine Learning"],
  "experience_years": 7.5,
  "education": [
    {
      "degree": "M.S. Computer Science",
      "institution": "MIT",
      "year": 2016
    }
  ],
  "ats_data": {
    "source": "LinkedIn",
    "application_date": "2024-01-15",
    "status": "screening"
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 789,
  "external_id": "GH-12345",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  ...
}
```

#### GET /ats/candidates
Pull candidates from platform (incremental sync).

**Headers:** `X-API-Key: <ats_api_key>`

**Rate Limit:** 1000 requests/hour

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50): Items per page
- `updated_since` (ISO datetime, optional): Only candidates updated after this timestamp

**Response:** `200 OK`
```json
{
  "total": 150,
  "candidates": [...],
  "page": 1,
  "page_size": 50
}
```

#### GET /ats/scorecards/export
Export interview scorecards to ATS (with bias filtering).

**Headers:** `X-API-Key: <ats_api_key>`

**Rate Limit:** 1000 requests/hour

**Query Parameters:**
- `candidate_external_id` (string, optional): Filter by candidate
- `from_date` (ISO datetime, optional): Start date
- `to_date` (ISO datetime, optional): End date

**Response:** `200 OK`
```json
[
  {
    "candidate_external_id": "GH-12345",
    "interview_date": "2024-02-01T10:00:00Z",
    "position": "Senior Software Engineer",
    "scores": {
      "technical": 85,
      "communication": 90,
      "cultural_fit": 88,
      "overall": 87.5
    },
    "recommendation": "recommend",
    "feedback": "Excellent candidate with strong technical skills...",
    "recruiter_email": "recruiter@company.com"
  }
]
```

#### POST /ats/feedback/sync
Sync additional feedback from ATS (with bias checking).

**Headers:** `X-API-Key: <ats_api_key>`

**Rate Limit:** 1000 requests/hour

**Query Parameters:**
- `candidate_external_id` (string, required): Candidate identifier

**Request Body:**
```json
{
  "text": "Great candidate with strong problem-solving skills",
  "source": "Greenhouse",
  "rating": 4.5,
  "reviewer": "Hiring Manager"
}
```

**Response:** `201 Created`
```json
{
  "status": "success",
  "candidate_id": 789,
  "bias_filtered": false
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Required roles: ['admin', 'hiring_manager']"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

**Headers:**
```
Retry-After: 3600
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706799600
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "type": "Exception"
}
```

---

## Rate Limiting

- **ATS Endpoints**: 1000 requests per hour per API key
- **Dashboard Endpoints**: No explicit rate limiting (authenticated users)

Rate limit headers are included in all ATS endpoint responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Bias Detection

All scorecard and feedback endpoints automatically check for bias. Flagged categories include:
- Age-related language
- Gender-specific terms
- Race/ethnicity references
- Disability mentions
- Appearance-based comments
- Family status references

**Example Bias Response:**
```json
{
  "bias_check_passed": false,
  "bias_flags": {
    "passed": false,
    "flags": [
      {
        "category": "age",
        "keyword": "young",
        "context": "...young and energetic candidate..."
      }
    ],
    "suggestions": [
      {
        "original": "young",
        "alternative": "early-career"
      }
    ],
    "severity": "medium"
  }
}
```

---

## WebSocket Protocol

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/api/recruiter/ws/interview/123');
```

### Message Handling
```javascript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'whisper':
      // Display AI suggestion
      break;
    case 'transcript':
      // Update live transcript
      break;
    case 'status':
      // Update interview status
      break;
  }
};
```

### Sending Messages
```javascript
ws.send(JSON.stringify({
  type: 'control',
  action: 'pause'
}));
```

---

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI JSON: `http://localhost:8000/api/openapi.json`
