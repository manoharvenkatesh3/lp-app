# Deployment Notes

## AWS (ECS + RDS)

1. Build Docker images and push to ECR:
   ```bash
   aws ecr create-repository --repository-name super-agent-backend
   aws ecr create-repository --repository-name super-agent-frontend
   docker build -t backend:latest backend
   docker build -t frontend:latest frontend
   ```
2. Provision RDS PostgreSQL 16 with the `pgvector` extension enabled.
3. Store secrets in AWS Secrets Manager and inject via ECS task definitions.
4. Use Application Load Balancer with health checks against `/healthz`.
5. Enable AWS Distro for OpenTelemetry (ADOT) to ship traces/logs.

## GCP (Cloud Run + Cloud SQL)

1. Build and push images to Artifact Registry.
2. Create Cloud SQL PostgreSQL instance and enable pgvector extension.
3. Deploy Cloud Run services for backend and frontend, referencing secrets from Secret Manager.
4. Configure Serverless VPC Access connector for private DB connectivity.
5. Enable Cloud Trace + Cloud Logging for observability.

## Terraform Modules

- `modules/network` – VPC, subnets, security groups
- `modules/database` – Postgres/pgvector provisioning
- `modules/app` – ECS services or Cloud Run services
- `modules/observability` – OTEL collectors, logging sinks

## Runbooks

- **Database migration**: `docker compose run --rm backend alembic upgrade head`
- **Rotate secrets**: Update Secret Manager entry, redeploy services
- **Scale workers**: Increase replica count on ECS service or GCP Cloud Run revision

## Monitoring

- Establish SLOs for API latency (P95 < 300ms) and error rate (<1%).
- Wire alerts to Slack/Teams via Webhooks.
- Collect structured logs (JSON) and traces via OpenTelemetry collector.
