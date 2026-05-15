export default function ObservabilityPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Observability</h1>
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
          <h2 className="text-lg font-semibold mb-4">Infrastructure Traces</h2>
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
        <div>
          <h2 className="text-lg font-semibold mb-4">Agent Events</h2>
          <div className="border border-gray-200 rounded-lg p-6">
            <p className="text-gray-400 text-sm">
              Agent execution events will appear here. Events are ingested via the Observer service.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
