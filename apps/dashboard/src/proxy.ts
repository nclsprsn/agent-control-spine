import { auth } from "@/auth";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import Negotiator from "negotiator";
import { match } from "@formatjs/intl-localematcher";

export const locales = ["en", "fr"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "en";

function getLocale(request: NextRequest): Locale {
  const headers: Record<string, string> = {};
  request.headers.forEach((value, key) => {
    headers[key] = value;
  });
  const languages = new Negotiator({ headers }).languages();
  try {
    return match(languages, [...locales], defaultLocale) as Locale;
  } catch {
    return defaultLocale;
  }
}

export const proxy = auth(function handleRequest(req) {
  const { pathname } = req.nextUrl;

  const isAuthPath = pathname.startsWith("/api/auth");
  if (!isAuthPath && !req.auth) {
    const signInUrl = new URL("/api/auth/signin", req.nextUrl.origin);
    signInUrl.searchParams.set("callbackUrl", req.nextUrl.href);
    return NextResponse.redirect(signInUrl);
  }

  const hasLocale = locales.some(
    (l) => pathname.startsWith(`/${l}/`) || pathname === `/${l}`
  );
  if (hasLocale) return NextResponse.next();

  const locale = getLocale(req as NextRequest);
  const redirectUrl = new URL(req.nextUrl.href);
  redirectUrl.pathname = `/${locale}${pathname}`;
  return NextResponse.redirect(redirectUrl);
});

export const config = {
  matcher: ["/((?!_next|favicon.ico|.*\\..*).*)"],
};
