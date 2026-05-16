"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { signOutAction } from "@/app/actions";
import { apiFetch } from "@/lib/api";
import type { Conversation } from "@/lib/types";

interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

export function ConversationSidebar() {
  const t = useTranslations("sidebar");
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    apiFetch<PaginatedResponse<Conversation>>("/v1/conversations")
      .then((res) => setConversations(res.items))
      .catch(() => setConversations([]));
  }, []);

  const handleDelete = useCallback(
    async (e: React.MouseEvent, convId: string) => {
      e.preventDefault();
      e.stopPropagation();
      if (!confirm(t("deleteConfirm"))) return;
      try {
        await apiFetch(`/v1/conversations/${convId}`, { method: "DELETE" });
        setConversations((prev) => prev.filter((c) => c.id !== convId));
      } catch {
        // silently fail
      }
    },
    [t],
  );

  return (
    <aside className="w-56 border-r border-border bg-surface flex flex-col h-full">
      <div className="px-3 py-4">
        <Link
          href="/"
          className="flex items-center gap-2 px-3 py-2 text-[0.75rem] font-medium tracking-wide uppercase text-muted hover:text-foreground rounded-md hover:bg-surface-hover transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          {t("newChat")}
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 space-y-0.5">
        {conversations.length === 0 && (
          <p className="text-[0.75rem] text-muted/60 px-3 py-6 text-center">
            {t("noConversations")}
          </p>
        )}
        {conversations.map((conv) => (
          <div key={conv.id} className="group flex items-center rounded-md hover:bg-surface-hover transition-colors">
            <Link
              href={`/?conversation=${conv.id}`}
              className="flex-1 px-3 py-1.5 text-[0.8125rem] truncate text-muted hover:text-foreground transition-colors"
            >
              {conv.title ?? "Untitled"}
            </Link>
            <button
              onClick={(e) => handleDelete(e, conv.id)}
              className="shrink-0 p-1 mr-1 rounded opacity-0 group-hover:opacity-100 text-muted/60 hover:text-foreground transition-all"
              aria-label="Delete conversation"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        ))}
      </nav>

      <div className="px-3 py-3 border-t border-border flex items-center justify-between">
        <Link
          href="/history"
          className="text-[0.6875rem] text-muted hover:text-foreground transition-colors"
        >
          {t("history")}
        </Link>
        <form action={signOutAction}>
          <button
            type="submit"
            className="text-[0.6875rem] text-muted/60 hover:text-foreground transition-colors"
          >
            {t("signOut")}
          </button>
        </form>
      </div>
    </aside>
  );
}
