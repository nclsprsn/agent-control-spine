export const dynamic = "force-dynamic";

import { apiFetch } from "@/lib/api";
import type { Capability, Tool, PaginatedResponse } from "@/lib/types";

export default async function CatalogPage() {
  const [capabilities, tools] = await Promise.all([
    apiFetch<PaginatedResponse<Capability>>(
      "/v1/catalog/capabilities"
    ).catch(() => null),
    apiFetch<PaginatedResponse<Tool>>("/v1/catalog/tools").catch(() => null),
  ]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Catalog</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-lg font-semibold mb-4">
            Capabilities ({capabilities?.total ?? 0})
          </h2>
          {!capabilities || capabilities.items.length === 0 ? (
            <p className="text-gray-400 text-sm">
              No capabilities registered yet.
            </p>
          ) : (
            <div className="space-y-3">
              {capabilities.items.map((cap) => (
                <div
                  key={cap.id}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <h3 className="font-medium text-sm">{cap.name}</h3>
                  {cap.description && (
                    <p className="text-xs text-gray-500 mt-1">
                      {cap.description}
                    </p>
                  )}
                  {cap.tags.length > 0 && (
                    <div className="flex gap-1 mt-2">
                      {cap.tags.map((tag) => (
                        <span
                          key={tag}
                          className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-4">
            Tools ({tools?.total ?? 0})
          </h2>
          {!tools || tools.items.length === 0 ? (
            <p className="text-gray-400 text-sm">No tools registered yet.</p>
          ) : (
            <div className="space-y-3">
              {tools.items.map((tool) => (
                <div
                  key={tool.id}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <h3 className="font-medium text-sm">{tool.name}</h3>
                  {tool.description && (
                    <p className="text-xs text-gray-500 mt-1">
                      {tool.description}
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    {tool.provider && (
                      <span className="text-xs text-gray-400">
                        Provider: {tool.provider}
                      </span>
                    )}
                    {tool.tags.map((tag) => (
                      <span
                        key={tag}
                        className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
