"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { Conversation } from "@/lib/types";

interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

export function ConversationSidebar() {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    apiFetch<PaginatedResponse<Conversation>>("/v1/conversations")
      .then((res) => setConversations(res.items))
      .catch(() => setConversations([]));
  }, []);

  return (
    <aside className="w-64 border-r bg-gray-50 flex flex-col h-full">
      <div className="p-4 border-b">
        <Link
          href="/"
          className="block w-full text-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
        >
          New Chat
        </Link>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 && (
          <p className="text-xs text-gray-400 px-2 py-4 text-center">
            No conversations yet.
          </p>
        )}
        {conversations.map((conv) => (
          <Link
            key={conv.id}
            href={`/?conversation=${conv.id}`}
            className="block px-3 py-2 text-sm rounded-md hover:bg-gray-200 truncate"
          >
            {conv.title ?? "Untitled"}
          </Link>
        ))}
      </nav>
      <div className="p-4 border-t">
        <Link
          href="/history"
          className="text-xs text-gray-500 hover:text-gray-700"
        >
          View all history
        </Link>
      </div>
    </aside>
  );
}
