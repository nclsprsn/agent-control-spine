"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
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
  const t = useTranslations("chat");
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
      className="bg-transparent border border-border rounded-md px-2 py-1 text-[0.75rem] text-muted hover:text-foreground focus:outline-none focus:border-muted/50 transition-colors cursor-pointer"
    >
      <option value="">{t("defaultAgent")}</option>
      {agents.map((agent) => (
        <option key={agent.id} value={agent.id}>
          {agent.name} v{agent.version}
        </option>
      ))}
    </select>
  );
}
