import type { Session } from "next-auth";

export function hasRole(session: Session | null, ...roles: string[]): boolean {
  const userRoles = session?.roles ?? [];
  return roles.some((r) => userRoles.includes(r));
}
