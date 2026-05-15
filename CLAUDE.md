# CLAUDE.md — Agent Control Spine

## Project Overview

Enterprise control plane for AI agents. Monorepo with Python backend services (FastAPI), Next.js frontends, and infrastructure-as-code.

## Architecture

- **AgentGateway** (external, config only) — LLM routing, MCP, A2A, CEL policy, JWT auth
- **Keycloak** (external, realm config) — OIDC/OAuth2 identity provider
- **services/registry** — Agent CRUD, lifecycle, versioning (FastAPI)
- **services/catalog** — Capability/tool discovery, full-text search (FastAPI)
- **services/chat** — Pydantic AI orchestration, SSE streaming, conversations (FastAPI)
- **services/observer** — Event ingestion, OTel/NATS forwarding (FastAPI)
- **libs/spine-common** — Shared library: DB, logging, health, middleware, base models
- **apps/dashboard** — Admin UI (Next.js 16, React 19, Tailwind 4, Auth.js 5)
- **apps/chat** — Standalone chat interface (Next.js 16)
- **agents/** — Pydantic AI agent definitions

## Development Commands

```bash
make dev          # docker compose up --build -d
make down         # docker compose down -v
make test         # pytest
make lint         # ruff check + format check
make fmt          # ruff fix + format
make typecheck    # mypy strict
make migrate      # alembic migrations
```

## Code Standards

- Python 3.14, strict mypy, ruff linting
- 12-factor: all config via env vars (pydantic-settings), structured JSON logs to stdout, stateless services
- FastAPI services follow pattern: config.py → models.py → schemas.py → service.py → routes.py → main.py
- Async everywhere: asyncpg, async SQLAlchemy, async httpx
- All backing services (DB, Redis, NATS) referenced by URL env vars

## Key Patterns

- **Config**: `pydantic-settings` BaseSettings subclass per service, loads from env
- **Database**: async SQLAlchemy engine from `DATABASE_URL`, session via async context manager
- **Health**: `/healthz` (liveness) + `/readyz` (readiness with DB check)
- **Logging**: structlog → JSON → stdout, OTel trace ID correlation
- **Auth**: Keycloak JWTs validated by AgentGateway (gateway-level) and middleware (service-level)

## Workspace Structure

uv workspace with members: `services/*`, `libs/*`, `agents`. Shared dev deps in root pyproject.toml.

## Docker

16 containers: postgres, redis, nats, keycloak, agentgateway, otel-collector, tempo, loki, prometheus, grafana + registry, catalog, observer, chat, dashboard, chat-app.
