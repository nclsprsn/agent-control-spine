"use client";

import { useState } from "react";
import type { ToolCall } from "@/lib/types";

export function ToolCallCard({ toolCall }: { toolCall: ToolCall }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-gray-300 rounded-md bg-white text-sm">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-gray-50"
      >
        <span className="flex items-center gap-2">
          <span className="font-mono text-xs bg-gray-100 px-1.5 py-0.5 rounded">
            {toolCall.name}
          </span>
          {toolCall.status === "running" && (
            <span className="text-yellow-600 text-xs">Running...</span>
          )}
          {toolCall.status === "error" && (
            <span className="text-red-600 text-xs">Error</span>
          )}
        </span>
        <span className="text-gray-400 text-xs">{expanded ? "▲" : "▼"}</span>
      </button>
      {expanded && (
        <div className="border-t px-3 py-2 space-y-2">
          {toolCall.args && (
            <div>
              <p className="text-xs text-gray-500 mb-1">Arguments</p>
              <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                {JSON.stringify(toolCall.args, null, 2)}
              </pre>
            </div>
          )}
          {toolCall.result && (
            <div>
              <p className="text-xs text-gray-500 mb-1">Result</p>
              <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                {toolCall.result}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
