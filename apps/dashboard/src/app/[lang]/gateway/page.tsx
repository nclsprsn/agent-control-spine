export const dynamic = "force-dynamic";

import { notFound } from "next/navigation";
import { getDictionary } from "../dictionaries";
import { locales } from "@/proxy";
import type { Locale } from "@/proxy";

const SERVICES = [
  {
    name: "Registry",
    envUrl: process.env.REGISTRY_URL || "http://localhost:8081",
    routes: ["/v1/agents"],
  },
  {
    name: "Catalog",
    envUrl: process.env.CATALOG_URL || "http://localhost:8082",
    routes: ["/v1/catalog/capabilities", "/v1/catalog/tools", "/v1/catalog/search"],
  },
  {
    name: "Observer",
    envUrl: process.env.OBSERVER_URL || "http://localhost:8083",
    routes: ["/v1/events", "/v1/traces"],
  },
  {
    name: "Chat",
    envUrl: process.env.CHAT_URL || "http://localhost:8084",
    routes: ["/v1/conversations", "/v1/chat"],
  },
];

type HealthStatus = "ready" | "degraded" | "down";

type HealthResult = {
  name: string;
  status: HealthStatus;
  latencyMs: number | null;
};

async function checkHealth(name: string, url: string): Promise<HealthResult> {
  const start = Date.now();
  try {
    const res = await fetch(`${url}/readyz`, {
      cache: "no-store",
      signal: AbortSignal.timeout(2000),
    });
    const latencyMs = Date.now() - start;
    if (res.ok) return { name, status: "ready", latencyMs };

    const liveness = await fetch(`${url}/healthz`, {
      cache: "no-store",
      signal: AbortSignal.timeout(2000),
    }).catch(() => null);
    return {
      name,
      status: liveness?.ok ? "degraded" : "down",
      latencyMs,
    };
  } catch {
    return { name, status: "down", latencyMs: null };
  }
}

const BADGE_CLASS: Record<HealthStatus, string> = {
  ready: "bg-green-100 text-green-700",
  degraded: "bg-yellow-100 text-yellow-700",
  down: "bg-red-100 text-red-700",
};

export default async function GatewayPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  if (!locales.includes(lang as Locale)) notFound();

  const dict = await getDictionary(lang as Locale);
  const t = dict.gateway;

  const results = await Promise.all(
    SERVICES.map((s) => checkHealth(s.name, s.envUrl))
  );
  const healthByName = Object.fromEntries(results.map((r) => [r.name, r]));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">{t.title}</h1>
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-3">{t.agentgateway}</h2>
          <div className="border border-gray-200 rounded-lg p-6">
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-gray-500">{t.fields.endpoint}</dt>
                <dd className="font-mono">
                  {process.env.INTERNAL_API_URL || "http://localhost:8080"}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">{t.fields.authMode}</dt>
                <dd>{t.fields.authModeValue}</dd>
              </div>
              <div>
                <dt className="text-gray-500">{t.fields.policyEngine}</dt>
                <dd>{t.fields.policyEngineValue}</dd>
              </div>
              <div>
                <dt className="text-gray-500">{t.fields.protocol}</dt>
                <dd>{t.fields.protocolValue}</dd>
              </div>
            </dl>
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-3">{t.upstreamHealth}</h2>
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium">{t.columns.service}</th>
                  <th className="text-left px-4 py-3 font-medium">{t.columns.status}</th>
                  <th className="text-left px-4 py-3 font-medium">{t.columns.latency}</th>
                  <th className="text-left px-4 py-3 font-medium">{t.columns.routes}</th>
                </tr>
              </thead>
              <tbody>
                {SERVICES.map((svc) => {
                  const h = healthByName[svc.name];
                  return (
                    <tr key={svc.name} className="border-t">
                      <td className="px-4 py-3 font-medium">{svc.name}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${BADGE_CLASS[h.status]}`}
                        >
                          {t.status[h.status]}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-500 font-mono">
                        {h.latencyMs !== null ? `${h.latencyMs}ms` : "—"}
                      </td>
                      <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                        {svc.routes.join(", ")}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
