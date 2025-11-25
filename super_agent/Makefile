.PHONY: help bootstrap up down logs test-backend test-frontend lint format clean

help:
	@echo "Super Agent Platform - Makefile Targets"
	@echo "----------------------------------------"
	@echo "  bootstrap       Install backend + frontend dependencies locally"
	@echo "  up              Start Docker Compose stack"
	@echo "  down            Stop Docker Compose stack"
	@echo "  logs            Tail Docker logs"
	@echo "  test-backend    Run backend pytest suite"
	@echo "  test-frontend   Run frontend tests (placeholder)"
	@echo "  lint            Lint backend and frontend"
	@echo "  format          Auto-format code"
	@echo "  clean           Remove build artifacts"

bootstrap:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Done. Run 'pre-commit install' to enable hooks."

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

test-backend:
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend:
	@echo "Frontend tests not configured yet. Add Vitest later."

lint:
	cd backend && ruff check app/ || echo "Ruff not installed. Skipping backend lint."
	cd frontend && npm run lint || echo "Prettier check failed or not configured."

format:
	cd backend && ruff check --fix app/ || echo "Ruff not installed. Skipping backend format."
	cd frontend && npm run format || echo "Prettier format failed or not configured."

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	docker compose down -v
