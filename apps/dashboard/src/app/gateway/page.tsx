export default function GatewayPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Gateway Configuration</h1>
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-3">AgentGateway</h2>
          <div className="border border-gray-200 rounded-lg p-6">
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-gray-500">Status</dt>
                <dd className="font-medium">Configured</dd>
              </div>
              <div>
                <dt className="text-gray-500">Endpoint</dt>
                <dd className="font-mono">http://localhost:8080</dd>
              </div>
              <div>
                <dt className="text-gray-500">Auth Provider</dt>
                <dd>Keycloak (OIDC)</dd>
              </div>
              <div>
                <dt className="text-gray-500">Policy Engine</dt>
                <dd>CEL</dd>
              </div>
            </dl>
          </div>
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-3">Upstream Targets</h2>
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3">Target</th>
                  <th className="text-left px-4 py-3">URL</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: "Registry", url: "http://registry:8081" },
                  { name: "Catalog", url: "http://catalog:8082" },
                  { name: "Observer", url: "http://observer:8083" },
                  { name: "Chat", url: "http://chat:8084" },
                ].map((target) => (
                  <tr key={target.name} className="border-t">
                    <td className="px-4 py-3 font-medium">{target.name}</td>
                    <td className="px-4 py-3 font-mono text-gray-500">{target.url}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
