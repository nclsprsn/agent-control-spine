export const dynamic = "force-dynamic";

import { notFound } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { getDictionary } from "../dictionaries";
import { locales } from "@/proxy";
import type { Locale } from "@/proxy";
import type { Agent, PaginatedResponse } from "@/lib/types";

export default async function AgentsPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  if (!locales.includes(lang as Locale)) notFound();

  const dict = await getDictionary(lang as Locale);
  const t = dict.agents;

  const data = await apiFetch<PaginatedResponse<Agent>>("/v1/agents/").catch(
    () => null
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t.title}</h1>
      </div>
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left px-4 py-3 font-medium">{t.columns.name}</th>
              <th className="text-left px-4 py-3 font-medium">{t.columns.version}</th>
              <th className="text-left px-4 py-3 font-medium">{t.columns.status}</th>
              <th className="text-left px-4 py-3 font-medium">{t.columns.owner}</th>
              <th className="text-left px-4 py-3 font-medium">{t.columns.description}</th>
            </tr>
          </thead>
          <tbody>
            {!data || data.items.length === 0 ? (
              <tr className="border-t">
                <td className="px-4 py-8 text-center text-gray-400" colSpan={5}>
                  {t.empty}
                </td>
              </tr>
            ) : (
              data.items.map((agent) => (
                <tr key={agent.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <Link
                      href={`/${lang}/agents/${agent.id}`}
                      className="text-blue-600 hover:underline font-medium"
                    >
                      {agent.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 font-mono text-gray-500">
                    {agent.version}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                        agent.status === "active"
                          ? "bg-green-100 text-green-700"
                          : agent.status === "registered"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {agent.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">{agent.owner}</td>
                  <td className="px-4 py-3 text-gray-500 max-w-xs truncate">
                    {agent.description}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {data && (
        <p className="text-xs text-gray-400 mt-3">
          {data.total === 1
            ? t.totalSingular.replace("{{count}}", String(data.total))
            : t.totalPlural.replace("{{count}}", String(data.total))}
        </p>
      )}
    </div>
  );
}
