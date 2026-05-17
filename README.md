# Agent Control Spine

Enterprise control plane for AI agents — gateway, registry, catalog, observability, and chat.

## Architecture

```
┌────────────────────────────┐  ┌─────────────────────────────────┐
│    Chat App (Next.js)      │  │    Admin Dashboard (Next.js)    │
│         :3002              │  │         :3001                    │
└────────────┬───────────────┘  └──────────────┬──────────────────┘
             │         ┌──────────┐             │
             │         │ Keycloak │             │
             │         │  :8443   │             │
             │         └────┬─────┘             │
     ┌───────▼──────────────▼───────────────────▼─────────────────┐
     │                    AgentGateway :8080                        │
     │  LLM routing · MCP · A2A · CEL policy · JWT auth · OTel     │
     └───┬──────────┬──────────────┬──────────────┬───────────────┘
   ┌─────▼────┐ ┌──▼──────┐ ┌────▼────┐ ┌──────▼─────┐
   │   Chat   │ │Registry │ │ Catalog │ │  Observer   │
   │  :8084   │ │  :8081  │ │  :8082  │ │   :8083     │
   └──────────┘ └─────────┘ └─────────┘ └────────────┘
         PostgreSQL :5432 · Redis :6379 · NATS :4222
         Grafana :3000 · Prometheus :9090 · Tempo · Loki
```

## Components

| Component | Tech | Purpose |
|-----------|------|---------|
| **AgentGateway** | [AgentGateway](https://agentgateway.dev) | LLM routing, MCP federation, A2A, policy-as-code (CEL), JWT auth |
| **Keycloak** | Keycloak 26 | Identity provider, OIDC/OAuth2, RBAC |
| **Registry** | FastAPI | Agent registration, versioning, lifecycle management |
| **Catalog** | FastAPI | Agent/capability/tool discovery, full-text search |
| **Chat** | FastAPI + Pydantic AI | Agent orchestration, SSE streaming, conversation management |
| **Observer** | FastAPI | Event ingestion, OTel trace forwarding |
| **Dashboard** | Next.js 16 | Admin UI for registry, catalog, observability, gateway |
| **Chat App** | Next.js 16 | Standalone conversational interface with agents |

## Quick Start

```bash
# Clone and configure
cp .env.example .env

# Start all services (16 containers)
make dev

# Verify
curl http://localhost:8081/healthz    # Registry
curl http://localhost:8082/healthz    # Catalog
curl http://localhost:8084/healthz    # Chat
open http://localhost:3001            # Dashboard (sign in: admin/admin, operator/operator, viewer/viewer)
open http://localhost:3002            # Chat App
open http://localhost:3000            # Grafana
open http://localhost:8443            # Keycloak Admin
```

## Development

```bash
make dev          # Start all services
make down         # Stop and remove volumes
make test         # Run tests
make lint         # Lint (ruff check + format)
make fmt          # Auto-format
make typecheck    # mypy strict mode
make migrate      # Run DB migrations
make seed         # Seed sample data
make logs         # Tail all logs
make clean        # Full cleanup
```

## 12-Factor App

This project follows the [12-factor methodology](https://12factor.net):

- **Config**: All configuration via environment variables (`pydantic-settings`)
- **Backing services**: PostgreSQL, Redis, NATS, Keycloak — attached resources via URL
- **Processes**: All services stateless — state in PostgreSQL/Redis
- **Logs**: Structured JSON to stdout via `structlog`
- **Admin processes**: Migrations and seeds as one-off scripts

## Tech Stack

- **Python 3.14** + uv workspace
- **FastAPI** + SQLAlchemy 2 + asyncpg
- **Pydantic AI** for agent orchestration
- **Next.js 16** + React 19 + Tailwind 4 + Auth.js 5
- **PostgreSQL 18** + Redis 8 + NATS 2.14
- **OpenTelemetry** + Grafana + Tempo + Loki + Prometheus
- **Terraform** for cloud IaC

## License

MIT
