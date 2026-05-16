"use client";

import { useState, useRef, useCallback } from "react";
import { useTranslations } from "next-intl";
import { AgentSelector } from "@/components/chat/agent-selector";
import { MessageList } from "@/components/chat/message-list";
import { MessageInput } from "@/components/chat/message-input";
import type { ChatMessage } from "@/lib/types";
import { streamChat } from "@/lib/streaming";

export default function ChatPage() {
  const t = useTranslations("common");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const handleSend = useCallback(
    async (content: string) => {
      if (!content.trim() || isStreaming) return;

      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      const assistantId = crypto.randomUUID();
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: "assistant", content: "", created_at: new Date().toISOString() },
      ]);

      setIsStreaming(true);
      abortRef.current = new AbortController();

      try {
        await streamChat(
          {
            message: content,
            agent_id: selectedAgent ?? undefined,
            conversation_id: conversationId ?? undefined,
          },
          {
            onThinkingDelta: (delta) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, thinking: (m.thinking ?? "") + delta } : m,
                ),
              );
            },
            onTextDelta: (delta) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: m.content + delta } : m,
                ),
              );
            },
            onToolCallStart: (toolCall) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, tool_calls: [...(m.tool_calls ?? []), { id: toolCall.call_id, name: toolCall.name, args: toolCall.args, status: "running" }] }
                    : m,
                ),
              );
            },
            onToolCallResult: (result) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? {
                        ...m,
                        tool_calls: m.tool_calls?.map((tc) =>
                          tc.id === result.call_id
                            ? { ...tc, result: result.result, status: "done" as const }
                            : tc,
                        ),
                      }
                    : m,
                ),
              );
            },
            onDone: (data) => {
              if (data.conversation_id) {
                setConversationId(data.conversation_id);
              }
            },
            signal: abortRef.current.signal,
          },
        );
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [isStreaming, selectedAgent, conversationId],
  );

  return (
    <div className="flex flex-col h-full">
      <header className="border-b border-border px-6 py-3 flex items-center justify-between shrink-0">
        <span className="text-[0.75rem] font-medium tracking-wide text-muted uppercase">{t("appName")}</span>
        <AgentSelector value={selectedAgent} onChange={setSelectedAgent} />
      </header>
      <MessageList messages={messages} isStreaming={isStreaming} />
      <MessageInput onSend={handleSend} disabled={isStreaming} />
    </div>
  );
}
