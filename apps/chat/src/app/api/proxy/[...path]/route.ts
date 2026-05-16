import { auth } from "@/auth";
import { NextRequest, NextResponse } from "next/server";

const GATEWAY_URL = process.env.GATEWAY_INTERNAL_URL || "http://localhost:8080";

async function proxyRequest(req: NextRequest) {
  const session = await auth();
  if (!session?.accessToken) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const path = req.nextUrl.pathname.replace("/api/proxy", "");
  const url = `${GATEWAY_URL}${path}${req.nextUrl.search}`;

  const headers: Record<string, string> = {
    "Authorization": `Bearer ${session.accessToken}`,
    "Content-Type": req.headers.get("content-type") || "application/json",
  };

  const userId = getUserIdFromToken(session.accessToken);
  if (userId) headers["x-user-id"] = userId;

  const res = await fetch(url, {
    method: req.method,
    headers,
    body: req.method !== "GET" && req.method !== "HEAD" ? await req.text() : undefined,
  });

  if (res.headers.get("content-type")?.includes("text/event-stream")) {
    return new Response(res.body, {
      status: res.status,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    });
  }

  const body = await res.text();
  return new Response(body, {
    status: res.status,
    headers: { "Content-Type": res.headers.get("content-type") || "application/json" },
  });
}

function getUserIdFromToken(token: string): string | undefined {
  try {
    const payload = token.split(".")[1];
    const claims = JSON.parse(Buffer.from(payload, "base64url").toString());
    return claims.sub || claims.preferred_username;
  } catch {
    return undefined;
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const PATCH = proxyRequest;
export const DELETE = proxyRequest;
