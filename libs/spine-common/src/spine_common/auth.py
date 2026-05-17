import time
from dataclasses import dataclass, field
from typing import Any

import httpx
import structlog
from fastapi import FastAPI, HTTPException, Request
from jose import JWTError, jwt

log = structlog.get_logger(__name__)

_TTL_SECONDS = 900  # 15 minutes


@dataclass
class Principal:
    sub: str
    username: str | None = None
    roles: list[str] = field(default_factory=list)
    raw_claims: dict[str, Any] = field(default_factory=dict)


class JWKSCache:
    def __init__(self, jwks_url: str, issuer: str, audience: str | None = None) -> None:
        self._client = httpx.AsyncClient()
        self._url = jwks_url
        self._issuer = issuer
        self._audience = audience
        self._cache: dict[str, Any] = {}
        self._fetched_at: float = 0.0

    async def _fetch(self) -> None:
        try:
            resp = await self._client.get(self._url, timeout=10.0)
            resp.raise_for_status()
            self._cache = {k["kid"]: k for k in resp.json()["keys"]}
            self._fetched_at = time.monotonic()
        except Exception:
            log.warning("jwks_fetch_failed", url=self._url, exc_info=True)
            raise

    def _decode(self, token: str) -> dict[str, Any]:
        options: dict[str, Any] = {"verify_aud": self._audience is not None}
        kwargs: dict[str, Any] = {
            "algorithms": ["RS256"],
            "issuer": self._issuer,
            "options": options,
        }
        if self._audience:
            kwargs["audience"] = self._audience
        return jwt.decode(token, {"keys": list(self._cache.values())}, **kwargs)  # type: ignore[no-any-return]

    async def verify(self, token: str) -> dict[str, Any]:
        now = time.monotonic()
        if not self._cache or now - self._fetched_at > _TTL_SECONDS:
            await self._fetch()

        try:
            header = jwt.get_unverified_header(token)
        except JWTError as exc:
            raise JWTError(f"Malformed token: {exc}") from exc

        kid = header.get("kid")
        if kid and kid not in self._cache:
            # Key rotation: try one refresh
            await self._fetch()

        return self._decode(token)

    async def close(self) -> None:
        await self._client.aclose()


def install_auth(
    app: FastAPI,
    jwks_url: str,
    issuer: str,
    audience: str | None = None,
    disabled: bool = False,
) -> JWKSCache | None:
    app.state.auth_disabled = disabled
    if disabled:
        app.state.jwks_cache = None
        return None
    cache = JWKSCache(jwks_url=jwks_url, issuer=issuer, audience=audience)
    app.state.jwks_cache = cache
    return cache


async def require_user(request: Request) -> Principal:
    if getattr(request.app.state, "auth_disabled", False):
        return Principal(sub="anonymous")

    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header[7:]
    cache: JWKSCache | None = getattr(request.app.state, "jwks_cache", None)
    if cache is None:
        raise HTTPException(status_code=503, detail="Auth not initialized")

    try:
        claims = await cache.verify(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except Exception as exc:
        log.warning("auth_verify_error", exc_info=True)
        raise HTTPException(status_code=401, detail="Token verification failed") from exc

    return Principal(
        sub=claims.get("sub", "unknown"),
        username=claims.get("preferred_username"),
        roles=claims.get("realm_access", {}).get("roles", []),
        raw_claims=claims,
    )
