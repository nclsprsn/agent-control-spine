export const dynamic = "force-dynamic";

import { promQuery } from "@/lib/prom";
import { DashboardCard } from "@/components/DashboardCard";

function fmt(value: number | null, decimals = 2): string {
  if (value === null) return "—";
  return value.toFixed(decimals);
}

export default async function ObservabilityPage() {
  const [reqPerSec, errorPct, p95LatencyMs, inFlight, perServiceRaw] =
    await Promise.all([
      promQuery("sum(rate(http_requests_total[5m]))"),
      promQuery(
        'sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100'
      ),
      promQuery(
        "histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m]))) * 1000"
      ),
      promQuery("sum(http_requests_inprogress)"),
      fetch(
        `${process.env.PROMETHEUS_URL || "http://localhost:9090"}/api/v1/query?query=${encodeURIComponent("sum by (job) (rate(http_requests_total[5m]))")}`,
        { cache: "no-store" }
      )
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null) as Promise<{
        status: string;
        data: { result: { metric: { job: string }; value: [number, string] }[] };
      } | null>,
    ]);

  const perService: { job: string; rps: string }[] =
    perServiceRaw?.status === "success"
      ? perServiceRaw.data.result.map((r) => ({
          job: r.metric.job,
          rps: parseFloat(r.value[1]).toFixed(3),
        }))
      : [];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Observability</h1>

      <div className="space-y-8">
        <div>
          <h2 className="text-lg font-semibold mb-4">Service Metrics</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <DashboardCard
              title="Requests / sec"
              value={fmt(reqPerSec, 2)}
              description="All services, 5m avg"
            />
            <DashboardCard
              title="Error rate"
              value={`${fmt(errorPct, 1)}%`}
              description="5xx responses, 5m avg"
            />
            <DashboardCard
              title="p95 latency"
              value={`${fmt(p95LatencyMs, 0)}ms`}
              description="Response time, 5m window"
            />
            <DashboardCard
              title="In-flight"
              value={fmt(inFlight, 0)}
              description="Active requests right now"
            />
          </div>

          {perService.length > 0 && (
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium">
                      Service
                    </th>
                    <th className="text-left px-4 py-3 font-medium">
                      Req / sec (5m)
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {perService.map((row) => (
                    <tr key={row.job} className="border-t">
                      <td className="px-4 py-3 font-medium">{row.job}</td>
                      <td className="px-4 py-3 font-mono text-gray-500">
                        {row.rps}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h2 className="text-lg font-semibold mb-4">LLM Traces (Langfuse)</h2>
            <div className="border border-gray-200 rounded-lg p-6">
              <p className="text-gray-400 text-sm mb-3">
                LLM call traces, token usage, latency, and evaluation scores.
              </p>
              <a
                href="http://localhost:3003"
                className="inline-block px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                target="_blank"
                rel="noopener noreferrer"
              >
                Open Langfuse
              </a>
            </div>
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-4">
              Infrastructure Traces
            </h2>
            <div className="border border-gray-200 rounded-lg p-6">
              <p className="text-gray-400 text-sm mb-3">
                Service-level traces, logs, and metrics via OpenTelemetry.
              </p>
              <a
                href="http://localhost:3000"
                className="inline-block px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                target="_blank"
                rel="noopener noreferrer"
              >
                Open Grafana
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
