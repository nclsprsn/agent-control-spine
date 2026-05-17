"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Locale } from "@/proxy";

type SidebarDict = {
  appName: string;
  appSubtitle: string;
  nav: {
    dashboard: string;
    agents: string;
    catalog: string;
    observability: string;
    gateway: string;
  };
  signOut: string;
};

const NAV_ITEMS = [
  { key: "dashboard" as const, href: "/", icon: "⌂" },
  { key: "agents" as const, href: "/agents", icon: "◎" },
  { key: "catalog" as const, href: "/catalog", icon: "▤" },
  { key: "observability" as const, href: "/observability", icon: "◉" },
  { key: "gateway" as const, href: "/gateway", icon: "⇄" },
];

export function Sidebar({
  locale,
  t,
  userName,
  signOutAction,
}: {
  locale: Locale;
  t: SidebarDict;
  userName: string | null;
  signOutAction: () => Promise<void>;
}) {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gray-950 text-gray-300 flex flex-col min-h-screen">
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-lg font-bold text-white">{t.appName}</h1>
        <p className="text-xs text-gray-500 mt-1">{t.appSubtitle}</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const fullHref =
            item.href === "/" ? `/${locale}` : `/${locale}${item.href}`;
          const isActive =
            item.href === "/"
              ? pathname === `/${locale}` || pathname === `/${locale}/`
              : pathname.startsWith(`/${locale}${item.href}`);
          return (
            <Link
              key={item.href}
              href={fullHref}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-gray-800 text-white"
                  : "hover:bg-gray-900 hover:text-white"
              }`}
            >
              <span className="text-base">{item.icon}</span>
              {t.nav[item.key]}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-800 space-y-2">
        {userName && (
          <p className="text-xs text-gray-400 truncate">{userName}</p>
        )}
        <form action={signOutAction}>
          <button
            type="submit"
            className="w-full text-left text-xs text-gray-500 hover:text-gray-300 transition-colors"
          >
            {t.signOut}
          </button>
        </form>
      </div>
    </aside>
  );
}
