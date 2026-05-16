export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  thinking?: string;
  tool_calls?: ToolCall[];
  created_at: string;
}

export interface ToolCall {
  id: string;
  name: string;
  args?: Record<string, unknown>;
  result?: string;
  status: "running" | "done" | "error";
}

export interface Conversation {
  id: string;
  title: string | null;
  agent_id: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface Agent {
  id: string;
  name: string;
  version: string;
  status: string;
  description: string | null;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  agent_id?: string;
}

export interface SSEEvent {
  event: string;
  data: string;
}
