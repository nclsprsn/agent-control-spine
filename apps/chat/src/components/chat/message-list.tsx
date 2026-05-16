"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import type { ChatMessage } from "@/lib/types";
import { Markdown } from "./markdown";
import { ToolCallCard } from "./tool-call-card";

function ElapsedTimer() {
  const t = useTranslations("chat");
  const [elapsed, setElapsed] = useState(0);
  const startRef = useRef<number | null>(null);

  useEffect(() => {
    startRef.current = Date.now();
    const interval = setInterval(() => {
      const start = startRef.current ?? Date.now();
      setElapsed(Math.floor((Date.now() - start) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  if (elapsed < 1) return null;
  return (
    <span className="text-[0.6875rem] text-muted/60 tabular-nums ml-1">
      {t("elapsed", { seconds: elapsed })}
    </span>
  );
}

function ThinkingIndicator({ hasContent }: { hasContent: boolean }) {
  const t = useTranslations("chat");
  return (
    <div className="flex items-center gap-2.5 py-1">
      <div className="relative flex items-center justify-center w-5 h-5">
        <span className="absolute inset-0 rounded-full border border-muted/30 animate-ping opacity-30" />
        <span className="w-2 h-2 rounded-full bg-muted/60 animate-[think-pulse_1.5s_ease-in-out_infinite]" />
      </div>
      <span className="text-[0.75rem] text-muted/60 italic tracking-wide">
        {t("thinking")}
      </span>
      {!hasContent && <ElapsedTimer />}
    </div>
  );
}

function ThinkingLivePreview({ content }: { content: string }) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [content]);

  return (
    <div className="mt-2 ml-2.5 pl-3 border-l border-muted/20 max-h-32 overflow-y-auto">
      <p className="text-[0.75rem] text-muted/40 italic leading-relaxed whitespace-pre-wrap">
        {content}
      </p>
      <div ref={endRef} />
    </div>
  );
}

function ThinkingBlock({ content, isActive }: { content: string; isActive: boolean }) {
  const [expanded, setExpanded] = useState(false);

  if (!content && !isActive) return null;

  if (isActive) {
    return (
      <div className="mb-4">
        <ThinkingIndicator hasContent={!!content} />
        {content && <ThinkingLivePreview content={content} />}
      </div>
    );
  }

  return (
    <div className="mb-4">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-[0.75rem] text-muted/40 hover:text-muted transition-colors group"
      >
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className={`transition-transform duration-200 ${expanded ? "rotate-90" : ""}`}
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <span className="italic group-hover:underline underline-offset-2">
          {content.length > 200 ? "Thought for a moment" : "Thought briefly"}
        </span>
      </button>
      {expanded && (
        <div className="mt-2 ml-2.5 pl-3 border-l border-muted/20 max-h-64 overflow-y-auto">
          <p className="text-[0.75rem] text-muted/40 italic leading-relaxed whitespace-pre-wrap">
            {content}
          </p>
        </div>
      )}
    </div>
  );
}

function StreamingCursor() {
  return (
    <span className="inline-block w-[0.125rem] h-[1em] bg-foreground/50 ml-0.5 animate-pulse align-middle rounded-full" />
  );
}

export function MessageList({
  messages,
  isStreaming,
}: {
  messages: ChatMessage[];
  isStreaming?: boolean;
}) {
  const t = useTranslations("chat");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-2">
        <p className="text-[0.875rem] text-muted/60">{t("emptyState")}</p>
      </div>
    );
  }

  const lastMessage = messages[messages.length - 1];

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
        {messages.map((msg) => {
          const isLast = msg.id === lastMessage?.id;

          if (msg.role === "user") {
            return (
              <div key={msg.id} className="flex justify-end">
                <div className="max-w-[75%] rounded-2xl rounded-br-sm px-4 py-2.5 text-[0.9375rem] bg-surface border border-border text-foreground leading-relaxed">
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            );
          }

          const isThinkingPhase = isLast && isStreaming && !msg.content && !!msg.thinking;
          const isWaiting = isLast && isStreaming && !msg.content && !msg.thinking;
          const isStreamingContent = isLast && isStreaming && !!msg.content;

          return (
            <div key={msg.id} className="flex justify-start">
              <div className="max-w-[85%] text-[0.9375rem] text-foreground/90">
                {isWaiting ? (
                  <ThinkingIndicator hasContent={false} />
                ) : (
                  <>
                    {msg.thinking && (
                      <ThinkingBlock
                        content={msg.thinking}
                        isActive={!!isThinkingPhase}
                      />
                    )}
                    {msg.content ? (
                      <>
                        <Markdown content={msg.content} />
                        {isStreamingContent && <StreamingCursor />}
                      </>
                    ) : null}
                    {msg.tool_calls && msg.tool_calls.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {msg.tool_calls.map((tc) => (
                          <ToolCallCard key={tc.id} toolCall={tc} />
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          );
        })}
        <div ref={endRef} />
      </div>
    </div>
  );
}
