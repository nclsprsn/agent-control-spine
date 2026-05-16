const INTERNAL_API_URL = process.env.INTERNAL_API_URL || "http://localhost:8080";
const KEYCLOAK_URL = process.env.KEYCLOAK_URL || "http://localhost:8443";
const KEYCLOAK_REALM = process.env.KEYCLOAK_REALM || "spine";
const KEYCLOAK_CLIENT_ID = process.env.KEYCLOAK_CLIENT_ID || "spine-services";
const KEYCLOAK_CLIENT_SECRET =
  process.env.KEYCLOAK_CLIENT_SECRET || "change-me-in-production";

let cachedToken: { token: string; expiresAt: number } | null = null;

async function getServiceToken(): Promise<string> {
  if (cachedToken && Date.now() < cachedToken.expiresAt - 30_000) {
    return cachedToken.token;
  }

  const tokenUrl = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/token`;
  const res = await fetch(tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "client_credentials",
      client_id: KEYCLOAK_CLIENT_ID,
      client_secret: KEYCLOAK_CLIENT_SECRET,
    }),
  });

  if (!res.ok) {
    throw new Error(`Keycloak token error: ${res.status}`);
  }

  const data = await res.json();
  cachedToken = {
    token: data.access_token,
    expiresAt: Date.now() + data.expires_in * 1000,
  };
  return cachedToken.token;
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const token = await getServiceToken();
  const res = await fetch(`${INTERNAL_API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options?.headers,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json() as Promise<T>;
}
