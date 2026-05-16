export const dynamic = "force-dynamic";

import { apiFetch } from "@/lib/api";
import type { Agent, Capability, Tool, PaginatedResponse } from "@/lib/types";

function DashboardCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <div className="border border-gray-200 rounded-lg p-6">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      <p className="text-xs text-gray-400 mt-1">{description}</p>
    </div>
  );
}

export default async function DashboardHome() {
  const [agents, capabilities, tools, conversations] = await Promise.all([
    apiFetch<PaginatedResponse<Agent>>("/v1/agents/?page_size=1").catch(
      () => null
    ),
    apiFetch<PaginatedResponse<Capability>>(
      "/v1/catalog/capabilities?page_size=1"
    ).catch(() => null),
    apiFetch<PaginatedResponse<Tool>>("/v1/catalog/tools?page_size=1").catch(
      () => null
    ),
    apiFetch<PaginatedResponse<unknown>>(
      "/v1/conversations?page_size=1"
    ).catch(() => null),
  ]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <DashboardCard
          title="Agents"
          value={agents ? String(agents.total) : "—"}
          description="Registered agents"
        />
        <DashboardCard
          title="Capabilities"
          value={capabilities ? String(capabilities.total) : "—"}
          description="Available capabilities"
        />
        <DashboardCard
          title="Tools"
          value={tools ? String(tools.total) : "—"}
          description="Registered tools"
        />
        <DashboardCard
          title="Conversations"
          value={conversations ? String(conversations.total) : "—"}
          description="Active conversations"
        />
      </div>
    </div>
  );
}
