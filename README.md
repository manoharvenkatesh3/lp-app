# lp-app / Super Agent Platform

This repository now includes the **Super Agent Platform**, a next-generation talent intelligence stack that complements the original loyalty program prototype. The platform is contained in the [`super_agent/`](./super_agent) directory and ships with:

- A modular **FastAPI** backend featuring dependency-injected services, SQLAlchemy models, Alembic migrations, structured logging, and OpenTelemetry hooks.
- A **React + TypeScript** frontend (Vite) with a global theme, responsive layout primitives, routing shell, and placeholder pages for the four core product modules plus ATS integrations.
- Infrastructure tooling (Docker Compose, Makefile scripts, pre-commit hooks, GitHub Actions templates) that target AWS/GCP-ready deployments and local DX productivity.

## Repository Layout

```
/home/engine/project
├── Resume_parser/              # Legacy Eureka AI app (unchanged)
├── streamlit_app.py            # Backward-compatible Streamlit entrypoint
└── super_agent/
    ├── backend/                # FastAPI application
    ├── frontend/               # React + TypeScript shell
    ├── infra/                  # Deployment notes, IaC placeholders, runbooks
    ├── docker-compose.yml      # Orchestrates Postgres, backend, frontend, worker
    ├── .env.example            # Environment variables for local + cloud
    ├── Makefile                # Developer workflows
    ├── .pre-commit-config.yaml # Shared linters and formatters
    └── .github/workflows/      # Lint/Test automation templates
```

## High-Level Architecture

| Layer      | Description |
|------------|-------------|
| Backend    | FastAPI app with modular routers (`/healthz`, `/api/v1/*`), SQLAlchemy models (candidates, resumes, interviews, transcripts, scorecards, audit logs), Alembic migrations, structlog-based logging, and OpenTelemetry instrumentation hooks. Services are dependency injected for testability and future extensibility (LLM agents, ATS bridges, scheduling workers). |
| Frontend   | Vite + React 18 + TypeScript UI featuring a themable design system, responsive shell, and placeholder routes for Intake, Screening, Interview Operations, Insights, and ATS Integrations. Global styles target “world-class” baseline aesthetics with CSS variables and utility layout primitives. |
| Data Layer | PostgreSQL 16 with the `pgvector` extension enabled for embedding similarity workflows. Connection details are centralized in `APP_DATABASE_URL` and surfaced to Alembic + SQLAlchemy via `pydantic-settings`. |
| Observability | Structured logging targets JSON output by default, enriched with request IDs. OpenTelemetry provides plug-and-play traces/metrics export to OTLP endpoints (AWS X-Ray, GCP Cloud Trace, etc.). |
| Infrastructure | Docker Compose powers local DX. GitHub Actions templates run lint + test for backend/frontend. Make targets wrap common actions (`make bootstrap`, `make up`, `make test-backend`, etc.). |

## Environment Variables

Copy `.env.example` to `.env` (Docker Compose automatically loads it). Key variables include:

| Variable | Purpose |
|----------|---------|
| `APP_ENV` | Runtime environment (`local`, `staging`, `prod`). |
| `APP_HOST` / `APP_PORT` | FastAPI host/port (default `0.0.0.0:8000`). |
| `APP_DATABASE_URL` | SQLAlchemy URL for Postgres/pgvector. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Optional OpenTelemetry OTLP collector URI. |
| `OPENROUTER_API_KEY` | LLM generation + reasoning (OpenRouter). |
| `DEEPGRAM_API_KEY` | Speech-to-text + streaming transcription. |
| `ZOOM_CLIENT_ID` / `ZOOM_CLIENT_SECRET` | Video conferencing ingest. |
| `GOOGLE_MEET_SERVICE_ACCOUNT` | Service account email for Meet automations. |
| `TEAMS_TENANT_ID` / `TEAMS_CLIENT_SECRET` | Microsoft Teams integration. |
| `ATS_API_KEY` / `ATS_BASE_URL` | External ATS bridge credentials. |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Database bootstrap values consumed by Docker Compose. |
| `VECTOR_DIMENSION` | Optional embedding dimension for pgvector columns. |

## Developer Workflows

1. **Bootstrap toolchains**
   ```bash
   cd super_agent
   make bootstrap
   pre-commit install
   ```

2. **Start the full stack** (migrations run automatically before the API boots):
   ```bash
   make up
   # or docker compose up --build
   ```
   - Backend reachable at `http://localhost:8000` (`/healthz`, `/docs`).
   - Frontend served from `http://localhost:5173` with hot reload.

3. **Run checks**
   ```bash
   make lint           # Ruff + Prettier
   make test-backend   # Pytest
   make test-frontend  # Vitest (placeholder script)
   ```

4. **Apply migrations** (if schema changes are introduced):
   ```bash
   cd super_agent/backend
   alembic revision -m "describe change"
   alembic upgrade head
   ```

5. **Deployment**
   - GitHub Actions templates (`.github/workflows/*.yml`) showcase how to orchestrate lint/test matrices for AWS/GCP container deploys.
   - Terraform / Helm specs live under `super_agent/infra`—start there when wiring cloud resources (ALB, ECS, GKE, etc.).

For deeper implementation details, see `super_agent/README.md` (coming soon) and per-service READMEs. Contributions should follow the pre-commit hooks and documentation guidelines above.
