import type { ChatRequest } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

interface StreamCallbacks {
  onTextDelta: (delta: string) => void;
  onToolCallStart: (toolCall: { call_id: string; name: string; args?: Record<string, unknown> }) => void;
  onToolCallResult: (result: { call_id: string; result: string }) => void;
  onDone?: () => void;
  signal?: AbortSignal;
}

export async function streamChat(request: ChatRequest, callbacks: StreamCallbacks): Promise<void> {
  const res = await fetch(`${API_URL}/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal: callbacks.signal,
  });

  if (!res.ok) {
    throw new Error(`Chat error: ${res.status} ${res.statusText}`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    let currentEvent = "";
    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        const data = line.slice(6);
        handleSSEEvent(currentEvent, data, callbacks);
        currentEvent = "";
      }
    }
  }
}

function handleSSEEvent(event: string, data: string, callbacks: StreamCallbacks): void {
  try {
    const parsed = JSON.parse(data);
    switch (event) {
      case "text_delta":
        callbacks.onTextDelta(parsed.content);
        break;
      case "tool_call_start":
        callbacks.onToolCallStart(parsed);
        break;
      case "tool_call_result":
        callbacks.onToolCallResult(parsed);
        break;
      case "done":
        callbacks.onDone?.();
        break;
    }
  } catch {
    if (event === "text_delta") {
      callbacks.onTextDelta(data);
    }
  }
}
