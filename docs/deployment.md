# Deployment Guide

Audience: Developers and deployment engineers.

## Prerequisites
- Git, Python, uv, Docker and Docker Compose.
- Configured PostgreSQL and LLM credentials.

## Configuration

| Variable | Purpose | Example |
|---|---|---|
| APP_ENVIRONMENT | Runtime mode | development |
| APP_BASE_PATH | Proxy path | Empty |
| APP_TIMEZONE | Time zone | UTC |
| POSTGRES_HOST | Database host | db |
| POSTGRES_PORT | Database port | 5432 |
| POSTGRES_DB | Database name | example |
| POSTGRES_USER | Application role | app_user |
| POSTGRES_PASSWORD | Database credential | Secret |
| SESSION_SECRET_KEY | Session signing | Generated secret |
| LLM_BASE_URL | Provider endpoint | Provider URL |
| LLM_MODEL | Model identifier | Provider model |
| LLM_API_KEY | Provider credential | Secret |
| LLM_TIMEOUT_SECONDS | Request timeout | 30 |

Use .env.example, app.env.example and agent.env.example.
Never commit actual credentials.

## Installation
    uv sync --locked
    docker compose -p day18 config --quiet

## Start existing configured deployment
    docker compose -p day18 up -d --wait --wait-timeout 120

## Verification
    docker compose -p day18 ps
    curl -f http://127.0.0.1:8081/health/ready

## Troubleshooting
- Database permission denied: check schema file permissions.
- Readiness failure: check database connectivity and credentials.
- Fresh deployment requires database role initialization.

## Rollback
Restore the previously tested image tag in Compose
and recreate the application container.
