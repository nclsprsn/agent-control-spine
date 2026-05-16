"use client";

import { useState } from "react";
import type { ToolCall } from "@/lib/types";

export function ToolCallCard({ toolCall }: { toolCall: ToolCall }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-border rounded-md bg-background text-sm">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-border/30 transition-colors"
      >
        <span className="flex items-center gap-2">
          <span className="font-mono text-xs bg-surface border border-border px-1.5 py-0.5 rounded text-foreground">
            {toolCall.name}
          </span>
          {toolCall.status === "running" && (
            <span className="text-yellow-400 text-xs">Running...</span>
          )}
          {toolCall.status === "error" && (
            <span className="text-red-400 text-xs">Error</span>
          )}
        </span>
        <span className="text-muted text-xs">{expanded ? "▲" : "▼"}</span>
      </button>
      {expanded && (
        <div className="border-t border-border px-3 py-2 space-y-2">
          {toolCall.args && (
            <div>
              <p className="text-xs text-muted mb-1">Arguments</p>
              <pre className="text-xs bg-surface p-2 rounded overflow-x-auto text-foreground/80">
                {JSON.stringify(toolCall.args, null, 2)}
              </pre>
            </div>
          )}
          {toolCall.result && (
            <div>
              <p className="text-xs text-muted mb-1">Result</p>
              <pre className="text-xs bg-surface p-2 rounded overflow-x-auto text-foreground/80">
                {toolCall.result}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
