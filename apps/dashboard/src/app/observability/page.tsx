export default function ObservabilityPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Observability</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-lg font-semibold mb-4">Recent Traces</h2>
          <div className="border border-gray-200 rounded-lg p-6">
            <p className="text-gray-400 text-sm">
              Traces will appear here once services are instrumented with OpenTelemetry.
              View detailed traces in{" "}
              <a href="http://localhost:3000" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
                Grafana
              </a>.
            </p>
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
