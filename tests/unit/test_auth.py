"""Unit tests for spine_common.auth JWT verification logic."""

import time
from typing import Annotated, Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from fastapi import Depends, FastAPI
from jose import JWTError, jwk, jwt
from spine_common.auth import JWKSCache, Principal, install_auth, require_user
from starlette.testclient import TestClient

TEST_ISSUER = "http://test-issuer/realms/test"
TEST_KID = "test-key-1"


def make_rsa_key() -> tuple[RSAPrivateKey, dict[str, Any]]:
    """Generate RSA key pair and return (private_key, JWK public key dict)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    jwk_pub = jwk.construct(public_pem, algorithm="RS256").to_dict()
    jwk_pub["kid"] = TEST_KID
    jwk_pub["alg"] = "RS256"
    return private_key, jwk_pub


def sign_token(
    private_key: RSAPrivateKey,
    claims: dict[str, Any],
    kid: str = TEST_KID,
) -> str:
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    return jwt.encode(
        claims,
        private_pem.decode(),
        algorithm="RS256",
        headers={"kid": kid},
    )


def make_cache(private_key: RSAPrivateKey, jwk_pub: dict[str, Any]) -> JWKSCache:
    cache = JWKSCache(jwks_url="http://fake/certs", issuer=TEST_ISSUER)
    cache._cache = {TEST_KID: jwk_pub}
    cache._fetched_at = time.monotonic()
    return cache


def valid_claims(exp_offset: int = 3600, roles: list[str] | None = None) -> dict[str, Any]:
    now = int(time.time())
    return {
        "sub": "user-123",
        "iss": TEST_ISSUER,
        "preferred_username": "alice",
        "realm_access": {"roles": roles if roles is not None else ["user"]},
        "iat": now,
        "exp": now + exp_offset,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_valid_token() -> None:
    private_key, jwk_pub = make_rsa_key()
    cache = make_cache(private_key, jwk_pub)
    token = sign_token(private_key, valid_claims())

    claims = await cache.verify(token)

    assert claims["sub"] == "user-123"
    assert claims["iss"] == TEST_ISSUER


@pytest.mark.asyncio
async def test_verify_expired_token() -> None:
    private_key, jwk_pub = make_rsa_key()
    cache = make_cache(private_key, jwk_pub)
    token = sign_token(private_key, valid_claims(exp_offset=-10))

    with pytest.raises(JWTError):
        await cache.verify(token)


@pytest.mark.asyncio
async def test_verify_wrong_issuer() -> None:
    private_key, jwk_pub = make_rsa_key()
    cache = make_cache(private_key, jwk_pub)
    claims = valid_claims()
    claims["iss"] = "http://wrong-issuer/realms/other"
    token = sign_token(private_key, claims)

    with pytest.raises(JWTError):
        await cache.verify(token)


@pytest.mark.asyncio
async def test_verify_wrong_signature() -> None:
    private_key, jwk_pub = make_rsa_key()
    other_key, _ = make_rsa_key()
    cache = make_cache(private_key, jwk_pub)
    token = sign_token(other_key, valid_claims())

    with pytest.raises(JWTError):
        await cache.verify(token)


@pytest.mark.asyncio
async def test_verify_malformed_token() -> None:
    private_key, jwk_pub = make_rsa_key()
    cache = make_cache(private_key, jwk_pub)

    with pytest.raises(JWTError):
        await cache.verify("not.a.valid.jwt.token.at.all")


def test_install_auth_disabled() -> None:
    app = FastAPI()
    result = install_auth(app, jwks_url="http://x", issuer="http://y", disabled=True)

    assert result is None
    assert app.state.auth_disabled is True
    assert app.state.jwks_cache is None


def test_install_auth_enabled() -> None:
    app = FastAPI()
    result = install_auth(app, jwks_url="http://x/certs", issuer="http://y/realms/r")

    assert result is not None
    assert app.state.auth_disabled is False
    assert app.state.jwks_cache is result


def test_require_user_disabled_returns_anonymous() -> None:
    """When auth_disabled=True, require_user returns anonymous Principal."""

    app = FastAPI()
    install_auth(app, jwks_url="http://x", issuer="http://y", disabled=True)

    @app.get("/test")
    async def endpoint(p: Annotated[Principal, Depends(require_user)]) -> dict[str, str]:
        return {"sub": p.sub}

    with TestClient(app) as client:
        resp = client.get("/test")
    assert resp.status_code == 200
    assert resp.json()["sub"] == "anonymous"


def test_require_user_missing_token_returns_401() -> None:
    _, jwk_pub = make_rsa_key()

    app = FastAPI()
    jwks = install_auth(app, jwks_url="http://x", issuer=TEST_ISSUER, disabled=False)
    assert jwks is not None
    jwks._cache = {TEST_KID: jwk_pub}
    jwks._fetched_at = time.monotonic()

    @app.get("/test")
    async def endpoint(p: Annotated[Principal, Depends(require_user)]) -> dict[str, str]:
        return {"sub": p.sub}

    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/test")
    assert resp.status_code == 401


def test_require_user_valid_token_returns_principal() -> None:
    private_key, jwk_pub = make_rsa_key()

    app = FastAPI()
    jwks = install_auth(app, jwks_url="http://x", issuer=TEST_ISSUER, disabled=False)
    assert jwks is not None
    jwks._cache = {TEST_KID: jwk_pub}
    jwks._fetched_at = time.monotonic()

    @app.get("/test")
    async def endpoint(p: Annotated[Principal, Depends(require_user)]) -> dict[str, str | None]:
        return {"sub": p.sub, "username": p.username}

    token = sign_token(private_key, valid_claims())
    with TestClient(app) as client:
        resp = client.get("/test", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["sub"] == "user-123"
    assert data["username"] == "alice"
