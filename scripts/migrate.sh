#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Running Alembic migrations ==="

for svc in registry catalog chat; do
    echo "--- migrate: ${svc} ---"
    (cd "$ROOT/services/$svc" && uv run alembic upgrade head)
done

echo "=== All migrations complete ==="
