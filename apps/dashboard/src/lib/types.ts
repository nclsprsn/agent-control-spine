export interface Agent {
  id: string;
  name: string;
  version: string;
  status: "registered" | "active" | "suspended" | "deprecated" | "terminated";
  description: string | null;
  owner: string;
  endpoint_url: string | null;
  auth_config: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
  last_heartbeat_at: string | null;
  created_at: string;
  updated_at: string | null;
  created_by: string | null;
}

export interface Capability {
  id: string;
  agent_id: string | null;
  name: string;
  description: string | null;
  input_schema: Record<string, unknown> | null;
  output_schema: Record<string, unknown> | null;
  tags: string[];
  created_at: string;
  updated_at: string | null;
}

export interface Tool {
  id: string;
  name: string;
  description: string | null;
  provider: string | null;
  input_schema: Record<string, unknown> | null;
  output_schema: Record<string, unknown> | null;
  tags: string[];
  created_at: string;
  updated_at: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
