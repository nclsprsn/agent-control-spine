export const dynamic = "force-dynamic";

import { notFound } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { getDictionary } from "../../dictionaries";
import { locales } from "@/proxy";
import type { Locale } from "@/proxy";
import type { Agent } from "@/lib/types";

export default async function AgentDetailPage({
  params,
}: {
  params: Promise<{ lang: string; id: string }>;
}) {
  const { lang, id } = await params;
  if (!locales.includes(lang as Locale)) notFound();

  const dict = await getDictionary(lang as Locale);
  const t = dict.agentDetail;

  const agent = await apiFetch<Agent>(`/v1/agents/${id}`).catch(() => null);

  if (!agent) {
    return (
      <div>
        <Link
          href={`/${lang}/agents`}
          className="text-blue-600 hover:underline text-sm"
        >
          {t.backToAgents}
        </Link>
        <p className="text-gray-400 mt-4">{t.notFound}</p>
      </div>
    );
  }

  return (
    <div>
      <Link
        href={`/${lang}/agents`}
        className="text-blue-600 hover:underline text-sm"
      >
        {t.backToAgents}
      </Link>
      <h1 className="text-2xl font-bold mt-4 mb-6">{agent.name}</h1>
      <div className="border border-gray-200 rounded-lg p-6 space-y-4">
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-gray-500">{t.fields.status}</dt>
            <dd className="font-medium">{agent.status}</dd>
          </div>
          <div>
            <dt className="text-gray-500">{t.fields.version}</dt>
            <dd className="font-mono">{agent.version}</dd>
          </div>
          <div>
            <dt className="text-gray-500">{t.fields.owner}</dt>
            <dd>{agent.owner}</dd>
          </div>
          <div>
            <dt className="text-gray-500">{t.fields.created}</dt>
            <dd>{new Date(agent.created_at).toLocaleString(lang)}</dd>
          </div>
          {agent.endpoint_url && (
            <div>
              <dt className="text-gray-500">{t.fields.endpoint}</dt>
              <dd className="font-mono text-xs">{agent.endpoint_url}</dd>
            </div>
          )}
          {agent.description && (
            <div className="col-span-2">
              <dt className="text-gray-500">{t.fields.description}</dt>
              <dd>{agent.description}</dd>
            </div>
          )}
        </dl>
        {agent.metadata && Object.keys(agent.metadata).length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              {t.metadata}
            </h3>
            <pre className="bg-gray-50 rounded p-3 text-xs overflow-auto">
              {JSON.stringify(agent.metadata, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
