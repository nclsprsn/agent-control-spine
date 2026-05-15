"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { Agent } from "@/lib/types";

interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

export function AgentSelector({
  value,
  onChange,
}: {
  value: string | null;
  onChange: (agentId: string | null) => void;
}) {
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    apiFetch<PaginatedResponse<Agent>>("/v1/agents?status=active")
      .then((res) => setAgents(res.items))
      .catch(() => setAgents([]));
  }, []);

  return (
    <select
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value || null)}
      className="border border-gray-300 rounded-md px-3 py-1.5 text-sm bg-white"
    >
      <option value="">Auto (default agent)</option>
      {agents.map((agent) => (
        <option key={agent.id} value={agent.id}>
          {agent.name} v{agent.version}
        </option>
      ))}
    </select>
  );
}
