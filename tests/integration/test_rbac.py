"""Integration tests for gateway CEL RBAC policies.

Requires the full Docker stack to be running (make dev).
Each case hits the AgentGateway with a role-scoped token and asserts HTTP 200/403.
"""

import httpx
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.anyio]

_NULL_ID = "00000000-0000-0000-0000-000000000000"


def _authed(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(timeout=10.0) as c:
        yield c


# ---------------------------------------------------------------------------
# RBAC matrix
# Format: (description, method, path, role_fixture, expected_status)
# ---------------------------------------------------------------------------

RBAC_CASES: list[tuple[str, str, str, str | None, int]] = [
    # --- registry ---
    ("viewer GET agents", "GET", "/v1/agents/", "viewer_token", 200),
    ("viewer POST agent", "POST", "/v1/agents/", "viewer_token", 403),
    ("operator GET agents", "GET", "/v1/agents/", "operator_token", 200),
    ("operator POST agent", "POST", "/v1/agents/", "operator_token", 422),
    ("operator DELETE agent", "DELETE", f"/v1/agents/{_NULL_ID}", "operator_token", 403),
    ("admin DELETE agent", "DELETE", f"/v1/agents/{_NULL_ID}", "admin_token", 404),
    # --- catalog ---
    ("viewer GET catalog", "GET", "/v1/catalog/capabilities", "viewer_token", 200),
    ("viewer POST capability", "POST", "/v1/catalog/capabilities", "viewer_token", 403),
    ("operator POST capability", "POST", "/v1/catalog/capabilities", "operator_token", 422),
    (
        "admin DELETE capability",
        "DELETE",
        f"/v1/catalog/capabilities/{_NULL_ID}",
        "admin_token",
        404,
    ),
    # --- conversations ---
    ("viewer GET conversations", "GET", "/v1/conversations", "viewer_token", 200),
    (
        "viewer DELETE conversation",
        "DELETE",
        f"/v1/conversations/{_NULL_ID}",
        "viewer_token",
        403,
    ),
    (
        "operator DELETE conversation",
        "DELETE",
        f"/v1/conversations/{_NULL_ID}",
        "operator_token",
        404,
    ),
    # --- chat (all roles) — GET on POST-only root returns 405, proving authz passed ---
    ("viewer access chat", "GET", "/v1/chat", "viewer_token", 405),
    ("operator access chat", "GET", "/v1/chat", "operator_token", 405),
    # --- observer (all roles) — GET on POST-only endpoints returns 405, proving authz passed ---
    ("viewer GET events", "GET", "/v1/events", "viewer_token", 405),
    ("viewer GET traces", "GET", "/v1/traces", "viewer_token", 405),
    # --- no token ---
    ("no token GET agents", "GET", "/v1/agents/", None, 401),
]


@pytest.mark.parametrize(
    "description,method,path,token_fixture,expected",
    [(d, m, p, t, e) for d, m, p, t, e in RBAC_CASES],
    ids=[d for d, *_ in RBAC_CASES],
)
async def test_rbac(
    require_stack,
    request,
    client: httpx.AsyncClient,
    gateway_url: str,
    description: str,
    method: str,
    path: str,
    token_fixture: str | None,
    expected: int,
) -> None:
    headers: dict[str, str] = {}
    if token_fixture:
        token = request.getfixturevalue(token_fixture)
        headers = _authed(token)

    resp = await client.request(method, f"{gateway_url}{path}", headers=headers)
    assert resp.status_code == expected, (
        f"{description}: expected {expected}, got {resp.status_code}. Body: {resp.text[:200]}"
    )
