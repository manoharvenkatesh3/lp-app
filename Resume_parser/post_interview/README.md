# Post-Interview Analytics Module

A comprehensive post-interview analytics system for the Eureka AI Talent Discovery Engine that provides encrypted transcript processing, bias-free scoring, and audit logging.

## Features

### 🔐 Security & Encryption
- **AES-256 Encryption** for interview transcripts
- **SHA-256 Hashing** for integrity verification
- **HMAC Signatures** for tamper detection
- **RSA Key Pairs** for asymmetric encryption support

### 🎯 Bias-Free Analytics
- **Skills-focused evaluation** (no demographic analysis)
- **Three-axis scoring**: Technical Skills, Communication Clarity, Core Competency
- **Transparent methodology** with detailed scoring breakdown
- **No emotion inference** or demographic profiling

### 📊 Comprehensive Scoring
- **Multi-dimensional analysis** with configurable weights
- **Strengths/weaknesses extraction** with evidence
- **Job match percentage** calculation
- **Auto-generated feedback narratives**

### 🗄️ Database Integration
- **PostgreSQL persistence** with async support
- **Complete audit logging** for compliance
- **Background task processing** with retries
- **Role-based access control (RBAC)**

### 🚀 REST API
- **FastAPI endpoints** with automatic documentation
- **JWT authentication** with role-based permissions
- **Export functionality** (JSON/PDF)
- **Real-time task monitoring**

## Architecture

```
post_interview/
├── __init__.py              # Module exports
├── models.py                # Pydantic data models
├── crypto.py                # Encryption & hashing utilities
├── analytics.py             # Core analytics engine
├── database.py              # PostgreSQL integration
├── auth.py                  # RBAC & authentication
├── background.py            # Background task management
├── api.py                   # FastAPI endpoints
└── tests/                   # Comprehensive test suite
    ├── __init__.py
    ├── test_analytics.py     # Unit tests
    ├── test_api.py          # Integration tests
    └── test_fixtures.py     # Test utilities
```

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# The post-interview analytics requires these additional packages:
# - asyncpg>=0.28.0          # PostgreSQL async driver
# - cryptography>=41.0.0      # Encryption utilities
# - fastapi>=0.104.0          # REST API framework
# - uvicorn>=0.24.0           # ASGI server
# - python-jose[cryptography]  # JWT handling
# - passlib[bcrypt]>=1.7.4     # Password hashing
# - python-multipart>=0.0.6    # Form data handling
# - pytest>=7.4.0             # Testing framework
# - pytest-asyncio>=0.21.0    # Async testing
# - faker>=19.0.0              # Test data generation
```

### 2. Database Setup

```sql
-- Create database
CREATE DATABASE eureka_analytics;

-- Create user (optional)
CREATE USER eureka_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE eureka_analytics TO eureka_user;
```

### 3. Streamlit Integration

The post-interview analytics is integrated into the main Eureka application:

```python
# The new tab appears automatically in the Streamlit app
# Navigate to: 📊 Post-Interview Analytics
```

### 4. API Server

Start the standalone API server:

```bash
# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=eureka_analytics
export DB_USER=eureka_user
export DB_PASSWORD=your_password
export JWT_SECRET_KEY=your-jwt-secret-key

# Start server
python api_server.py --host 0.0.0.0 --port 8000

# API Documentation: http://localhost:8000/docs
```

## Usage Examples

### Python API Usage

```python
from post_interview import (
    AnalyticsConfig,
    InterviewAnalytics,
    TranscriptCrypto,
    TranscriptHasher,
    TranscriptProcessor
)

# Initialize components
config = AnalyticsConfig()
crypto = TranscriptCrypto()
hasher = TranscriptHasher()
processor = TranscriptProcessor(crypto, hasher)
analytics = InterviewAnalytics(config, processor)

# Process interview transcript
transcript_data = processor.process_transcript(
    transcript={
        "messages": [
            {"speaker": "Interviewer", "text": "Describe your Python experience."},
            {"speaker": "Candidate", "text": "I have 5 years of Python development experience."}
        ]
    },
    session_id="session_123",
    candidate_id="candidate_456",
    job_id="job_789",
    interview_type="technical",
    duration_minutes=45
)

# Generate scorecard
scorecard = analytics.analyze_interview(
    transcript_data,
    job_requirements=["Python", "Web Development", "API Design"]
)

print(f"Overall Score: {scorecard.overall_score}")
print(f"Job Match: {scorecard.job_match_percentage}%")
```

### REST API Usage

```bash
# Authenticate
curl -X POST "http://localhost:8000/api/v1/analytics/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"

# Get scorecard
curl -X GET "http://localhost:8000/api/v1/analytics/scorecards/session_123" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Export scorecard
curl -X POST "http://localhost:8000/api/v1/analytics/export/scorecards/session_123?export_format=json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Streamlit Interface

1. **Navigate to "📊 Post-Interview Analytics" tab**
2. **Input transcript** (manual entry, file upload, or sample data)
3. **Configure scoring weights** (skill, clarity, competency)
4. **Process analytics** with encrypted transcript handling
5. **View results** with detailed breakdown and export options

## Configuration

### Analytics Configuration

```python
from post_interview import AnalyticsConfig

config = AnalyticsConfig(
    skill_weight=0.4,        # Weight for technical skills
    clarity_weight=0.3,      # Weight for communication clarity
    competency_weight=0.3     # Weight for core competency
)
```

### Database Configuration

```python
from post_interview import DatabaseConfig

db_config = DatabaseConfig(
    host="localhost",
    port=5432,
    database="eureka_analytics",
    username="eureka_user",
    password="your_password"
)
```

### RBAC Roles

- **Admin**: Full access to all resources
- **Hiring Manager**: Read/write access to scorecards and analytics
- **Recruiter**: Read/write access to scorecards
- **Interviewer**: Access to own sessions and scorecards
- **Viewer**: Read-only access to assigned resources

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest Resume_parser/post_interview/tests/

# Run specific test file
pytest Resume_parser/post_interview/tests/test_analytics.py

# Run with coverage
pytest --cov=Resume_parser/post_interview Resume_parser/post_interview/tests/
```

### Test Coverage

The test suite includes:
- **Unit tests** for encryption, analytics, and scoring
- **Integration tests** for API endpoints and database
- **Synthetic data testing** for deterministic scoring
- **Edge case testing** for robustness
- **Performance testing** utilities

## Security Considerations

### Encryption
- Transcripts are encrypted using AES-256 in CBC mode
- Keys are derived using PBKDF2 with 100,000 iterations
- SHA-256 hashes ensure integrity
- HMAC signatures prevent tampering

### Authentication
- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Account lockout after failed attempts
- Role-based access control

### Audit & Compliance
- Complete audit trail for all operations
- Immutable logging with timestamps
- GDPR-compliant data handling
- No demographic or emotion-based analysis

## Performance

### Background Processing
- Async task processing with configurable workers
- Automatic retry with exponential backoff
- Task queue with priority support
- Observability and monitoring

### Database Optimization
- Connection pooling for performance
- Optimized indexes for common queries
- Batch operations for bulk processing
- Automatic cleanup of old tasks

## Monitoring & Observability

### Task Statistics
```python
stats = task_manager.get_task_statistics()
print(f"Success Rate: {stats['success_rate']}%")
print(f"Active Tasks: {stats['active_tasks']}")
```

### API Health Check
```bash
curl http://localhost:8000/health
```

### Database Statistics
```python
# Available through API
GET /api/v1/analytics/statistics
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Connection**: Check PostgreSQL configuration
3. **Authentication**: Verify JWT secret key is set
4. **Encryption**: Ensure crypto keys are properly initialized

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run API server with debug
python api_server.py --debug
```

## Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd eureka-talent-discovery

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest Resume_parser/post_interview/tests/

# Start development server
python api_server.py --reload --debug
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add comprehensive docstrings
- Include unit tests for new features

## License

This module is part of the Eureka AI Talent Discovery Engine and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test cases for usage examples
3. Consult the API documentation at `/docs`
4. Check the main application README for general guidance