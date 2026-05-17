import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Sidebar } from "@/components/layout/sidebar";
import { getDictionary } from "./dictionaries";
import { locales } from "@/proxy";
import type { Locale } from "@/proxy";
import { auth, signOut } from "@/auth";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ lang: string }>;
}): Promise<Metadata> {
  const { lang } = await params;
  if (!locales.includes(lang as Locale)) return {};
  const dict = await getDictionary(lang as Locale);
  return {
    title: dict.metadata.title,
    description: dict.metadata.description,
  };
}

export default async function LangLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  if (!locales.includes(lang as Locale)) notFound();

  const [dict, session] = await Promise.all([
    getDictionary(lang as Locale),
    auth(),
  ]);

  async function handleSignOut() {
    "use server";
    await signOut({ redirectTo: "/" });
  }

  return (
    <>
      <Sidebar
        locale={lang as Locale}
        t={dict.sidebar}
        userName={session?.user?.name ?? null}
        signOutAction={handleSignOut}
      />
      <main className="flex-1 p-8">{children}</main>
    </>
  );
}
