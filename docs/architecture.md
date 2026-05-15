# Architecture

## Overview

Agent Control Spine is an enterprise control plane for AI agents, providing gateway routing, agent registry, capability catalog, observability, and conversational interfaces.

## Components

### AgentGateway (External)
- LLM routing to 100+ providers via OpenAI-compatible API
- MCP server federation
- A2A (Agent-to-Agent) protocol support
- Policy-as-code via CEL engine
- JWT auth via Keycloak integration
- Rate limiting and OTel tracing

### Keycloak (External)
- OIDC/OAuth2 identity provider
- Realm: `spine`
- Clients: `spine-dashboard`, `spine-chat`, `spine-services`
- Roles: `admin`, `operator`, `viewer`

### Registry Service
- Agent CRUD and lifecycle management
- Status: registered → active → suspended → deprecated → terminated
- Versioning with changelog tracking
- Heartbeat monitoring

### Catalog Service
- Capability and tool registration
- Full-text search
- Tag-based filtering
- JSON Schema for input/output definitions

### Chat Service
- Pydantic AI-based agent orchestration
- SSE streaming for real-time responses
- Conversation persistence
- Tool call tracking and visibility

### Observer Service
- Agent execution event ingestion
- OTel trace forwarding
- NATS event publishing

## 12-Factor Compliance

See README.md for the full 12-factor mapping.

## Data Flow

1. User authenticates via Keycloak OIDC
2. Frontend sends request through AgentGateway
3. AgentGateway validates JWT, applies CEL policies
4. Request routed to appropriate backend service
5. Service processes request, emits OTel traces
6. Observer forwards events to OTel Collector and NATS
7. Grafana displays traces, metrics, and logs
