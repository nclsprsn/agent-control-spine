export const dynamic = "force-dynamic";

import { notFound } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { DashboardCard } from "@/components/DashboardCard";
import { getDictionary } from "./dictionaries";
import { locales } from "@/proxy";
import type { Locale } from "@/proxy";
import type { Agent, Capability, Tool, PaginatedResponse } from "@/lib/types";

export default async function DashboardHome({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  if (!locales.includes(lang as Locale)) notFound();

  const dict = await getDictionary(lang as Locale);
  const t = dict.home;

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
      <h1 className="text-2xl font-bold mb-6">{t.title}</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <DashboardCard
          title={t.agents.title}
          value={agents ? String(agents.total) : "—"}
          description={t.agents.description}
        />
        <DashboardCard
          title={t.capabilities.title}
          value={capabilities ? String(capabilities.total) : "—"}
          description={t.capabilities.description}
        />
        <DashboardCard
          title={t.tools.title}
          value={tools ? String(tools.total) : "—"}
          description={t.tools.description}
        />
        <DashboardCard
          title={t.conversations.title}
          value={conversations ? String((conversations as PaginatedResponse<unknown>).total) : "—"}
          description={t.conversations.description}
        />
      </div>
    </div>
  );
}
