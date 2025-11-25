# Super Agent Platform

A production-grade talent intelligence platform featuring:

- **FastAPI Backend** with SQLAlchemy, Alembic migrations, structured logging, and OpenTelemetry
- **React + TypeScript Frontend** (Vite) with responsive design system and modular routing
- **PostgreSQL + pgvector** for embeddings and similarity search
- **Docker Compose** orchestration with auto-migrations
- **Pre-commit hooks** and GitHub Actions for CI/CD

## Architecture

```
super_agent/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers (healthz, v1 endpoints)
│   │   ├── core/             # Config, logging, telemetry
│   │   ├── db/               # SQLAlchemy session + base
│   │   ├── models/           # ORM entities (Candidate, Resume, Interview, etc.)
│   │   ├── schemas/          # Pydantic request/response models
│   │   └── services/         # Business logic (dependency-injected)
│   ├── alembic/              # Migration scripts
│   ├── tests/                # Pytest suites
│   ├── requirements.txt      # Backend dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI primitives
│   │   ├── pages/            # Route components (Intake, Screening, etc.)
│   │   ├── services/         # API client, auth
│   │   ├── types/            # TypeScript interfaces
│   │   └── styles/           # Global theme, CSS variables
│   ├── public/               # Static assets
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── infra/
│   └── deployment-notes.md   # AWS/GCP guidance, Terraform snippets
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md                 # This file
```

## Environment Variables

All configuration is externalized via `.env`. Copy `.env.example` and customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `local` | Environment name |
| `APP_HOST` | `0.0.0.0` | FastAPI bind address |
| `APP_PORT` | `8000` | FastAPI port |
| `APP_DATABASE_URL` | `postgresql+psycopg2://...` | SQLAlchemy connection string |
| `APP_LOG_LEVEL` | `INFO` | structlog level |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _(empty)_ | OpenTelemetry collector endpoint |
| `OPENROUTER_API_KEY` | _(empty)_ | LLM API key |
| `DEEPGRAM_API_KEY` | _(empty)_ | Speech-to-text API key |
| `ZOOM_CLIENT_ID` | _(empty)_ | Zoom OAuth client ID |
| `ZOOM_CLIENT_SECRET` | _(empty)_ | Zoom OAuth secret |
| `GOOGLE_MEET_SERVICE_ACCOUNT` | _(empty)_ | Google Meet service account email |
| `TEAMS_TENANT_ID` | _(empty)_ | Microsoft Teams tenant ID |
| `TEAMS_CLIENT_SECRET` | _(empty)_ | Microsoft Teams client secret |
| `ATS_API_KEY` | _(empty)_ | External ATS integration key |
| `ATS_BASE_URL` | _(empty)_ | External ATS base URL |
| `POSTGRES_USER` | `superagent` | Database username |
| `POSTGRES_PASSWORD` | `superagent` | Database password |
| `POSTGRES_DB` | `superagent` | Database name |
| `VECTOR_DIMENSION` | `1536` | pgvector embedding dimension |

## Quick Start

### Prerequisites

- Docker 24+ with Compose plugin
- Python 3.11+ (for local backend dev)
- Node 20+ (for local frontend dev)
- Make (optional but recommended)

### 1. Bootstrap

```bash
# Clone and navigate
cd super_agent

# Copy environment template
cp .env.example .env

# Install pre-commit hooks (requires Python venv)
make bootstrap
pre-commit install
```

### 2. Start Stack

```bash
make up
# or: docker compose up --build
```

Services:
- **Backend**: `http://localhost:8000` (Swagger at `/docs`)
- **Frontend**: `http://localhost:5173` (Vite dev server)
- **PostgreSQL**: `localhost:5432`

The backend entrypoint runs migrations automatically before starting the server.

### 3. Verify Health

```bash
curl http://localhost:8000/healthz
# Expected: {"status":"ok","environment":"local","timestamp":"..."}
```

Open `http://localhost:5173` to see the frontend shell with placeholder routes.

### 4. Run Tests

```bash
make test-backend   # Pytest suite
make test-frontend  # Vitest (placeholder)
```

### 5. Lint & Format

```bash
make lint           # Ruff (backend) + Prettier (frontend)
make format         # Auto-fix
```

## Core Entities

| Model | Description |
|-------|-------------|
| `Candidate` | Personal information, contact details, ATS sync state |
| `Resume` | Document metadata, parsed text, embedding vectors |
| `Interview` | Scheduled sessions, video meeting links, status |
| `Transcript` | Speech-to-text output, timestamps, speaker labels |
| `Scorecard` | Evaluation criteria, scores, feedback, LLM annotations |
| `AuditLog` | Change tracking, user actions, system events |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Health check |
| `POST` | `/api/v1/candidates` | Create candidate |
| `GET` | `/api/v1/candidates` | List candidates (paginated) |
| `GET` | `/api/v1/candidates/{id}` | Get candidate details |
| `PATCH` | `/api/v1/candidates/{id}` | Update candidate |
| `POST` | `/api/v1/resumes/upload` | Upload and parse resume |
| `GET` | `/api/v1/interviews` | List interviews |
| `POST` | `/api/v1/interviews/{id}/transcribe` | Start transcription |
| `POST` | `/api/v1/scorecards` | Create scorecard |

## Frontend Routes

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | `Home` | Landing page with navigation |
| `/intake` | `IntakePage` | Candidate upload, ATS sync |
| `/screening` | `ScreeningPage` | Resume parsing, ranking |
| `/interviews` | `InterviewsPage` | Scheduling, transcription, scorecards |
| `/insights` | `InsightsPage` | Analytics dashboard |
| `/integrations` | `IntegrationsPage` | ATS configuration |

## Database Migrations

```bash
cd backend

# Create new migration
alembic revision -m "add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Development Workflows

### Backend Local Development

```bash
cd backend

# Install dependencies
poetry install

# Activate shell
poetry shell

# Run server (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Local Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## Deployment

### AWS (ECS + RDS)

1. Build and push images to ECR
2. Provision RDS PostgreSQL with pgvector
3. Configure ECS task definitions with environment variables
4. Set up ALB with health checks on `/healthz`
5. Configure CloudWatch for logs and X-Ray for traces

See `infra/deployment-notes.md` for Terraform examples.

### GCP (Cloud Run + Cloud SQL)

1. Build and push images to Artifact Registry
2. Provision Cloud SQL PostgreSQL with pgvector
3. Deploy Cloud Run services with secrets from Secret Manager
4. Configure Cloud Load Balancer
5. Enable Cloud Trace and Cloud Logging

## Observability

### Structured Logging

All logs are JSON-formatted with:
- `timestamp`
- `level`
- `message`
- `request_id` (for request correlation)
- `service` (backend identifier)

### OpenTelemetry

Set `OTEL_EXPORTER_OTLP_ENDPOINT` to export traces/metrics:
- AWS X-Ray: Use AWS Distro for OpenTelemetry
- GCP Cloud Trace: Use OpenTelemetry Collector with GCP exporter
- Jaeger/Zipkin: Self-hosted OTLP endpoint

## Contributing

1. Create feature branch from `main`
2. Make changes following code style guidelines
3. Run pre-commit hooks: `pre-commit run --all-files`
4. Test locally: `make test-backend test-frontend`
5. Open pull request with description and tests

## License

Proprietary - Internal Use Only
