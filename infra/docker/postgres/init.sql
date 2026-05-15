-- Agent Control Spine — Database Initialization
-- Creates tables for registry, catalog, and chat services

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Registry: Agents
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'registered',
    description TEXT,
    owner VARCHAR(255) NOT NULL,
    endpoint_url VARCHAR(2048),
    auth_config JSONB,
    metadata JSONB,
    last_heartbeat_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS ix_agents_name ON agents(name);
CREATE INDEX IF NOT EXISTS ix_agents_status ON agents(status);

-- Registry: Agent Versions
CREATE TABLE IF NOT EXISTS agent_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    version VARCHAR(50) NOT NULL,
    changelog TEXT,
    config_snapshot JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS ix_agent_versions_agent_id ON agent_versions(agent_id);

-- Catalog: Capabilities
CREATE TABLE IF NOT EXISTS capabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    input_schema JSONB,
    output_schema JSONB,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS ix_capabilities_name ON capabilities(name);
CREATE INDEX IF NOT EXISTS ix_capabilities_tags ON capabilities USING GIN(tags);

-- Catalog: Tools
CREATE TABLE IF NOT EXISTS tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    provider VARCHAR(255),
    input_schema JSONB,
    output_schema JSONB,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS ix_tools_name ON tools(name);
CREATE INDEX IF NOT EXISTS ix_tools_tags ON tools USING GIN(tags);

-- Chat: Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    agent_id UUID NOT NULL,
    title VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_conversations_user_id ON conversations(user_id);

-- Chat: Messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSONB,
    token_usage JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages(conversation_id);
