import { auth } from "@/auth";

const GATEWAY_URL = process.env.INTERNAL_API_URL || "http://localhost:8080";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const session = await auth();
  if (!session?.accessToken) {
    throw new ApiError("Unauthenticated", 401);
  }

  const res = await fetch(`${GATEWAY_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.accessToken}`,
      ...options?.headers,
    },
    cache: "no-store",
  });

  if (res.status === 403) throw new ApiError("Forbidden", 403);
  if (!res.ok) throw new ApiError(`${res.status} ${res.statusText}`, res.status);

  return res.json() as Promise<T>;
}
