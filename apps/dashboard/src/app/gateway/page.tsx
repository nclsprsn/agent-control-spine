export const dynamic = "force-dynamic";

const SERVICES = [
  {
    name: "Registry",
    url: process.env.REGISTRY_URL || "http://localhost:8081",
    routes: ["/v1/agents"],
  },
  {
    name: "Catalog",
    url: process.env.CATALOG_URL || "http://localhost:8082",
    routes: ["/v1/catalog/capabilities", "/v1/catalog/tools", "/v1/catalog/search"],
  },
  {
    name: "Observer",
    url: process.env.OBSERVER_URL || "http://localhost:8083",
    routes: ["/v1/events", "/v1/traces"],
  },
  {
    name: "Chat",
    url: process.env.CHAT_URL || "http://localhost:8084",
    routes: ["/v1/conversations", "/v1/chat"],
  },
];

type HealthResult = {
  name: string;
  status: "ready" | "degraded" | "down";
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

const STATUS_BADGE: Record<
  HealthResult["status"],
  { label: string; className: string }
> = {
  ready: { label: "ready", className: "bg-green-100 text-green-700" },
  degraded: { label: "degraded", className: "bg-yellow-100 text-yellow-700" },
  down: { label: "down", className: "bg-red-100 text-red-700" },
};

export default async function GatewayPage() {
  const results = await Promise.all(
    SERVICES.map((s) => checkHealth(s.name, s.url))
  );
  const healthByName = Object.fromEntries(results.map((r) => [r.name, r]));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Gateway Configuration</h1>
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-3">AgentGateway</h2>
          <div className="border border-gray-200 rounded-lg p-6">
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-gray-500">Endpoint</dt>
                <dd className="font-mono">
                  {process.env.INTERNAL_API_URL || "http://localhost:8080"}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">Auth Mode</dt>
                <dd>JWT strict (Keycloak RS256)</dd>
              </div>
              <div>
                <dt className="text-gray-500">Policy Engine</dt>
                <dd>CEL</dd>
              </div>
              <div>
                <dt className="text-gray-500">Protocol</dt>
                <dd>HTTP + MCP + A2A</dd>
              </div>
            </dl>
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-3">Upstream Health</h2>
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium">Service</th>
                  <th className="text-left px-4 py-3 font-medium">Status</th>
                  <th className="text-left px-4 py-3 font-medium">Latency</th>
                  <th className="text-left px-4 py-3 font-medium">
                    Gateway Routes
                  </th>
                </tr>
              </thead>
              <tbody>
                {SERVICES.map((svc) => {
                  const h = healthByName[svc.name];
                  const badge = STATUS_BADGE[h.status];
                  return (
                    <tr key={svc.name} className="border-t">
                      <td className="px-4 py-3 font-medium">{svc.name}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${badge.className}`}
                        >
                          {badge.label}
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
