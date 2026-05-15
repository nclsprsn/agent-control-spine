#!/usr/bin/env bash
set -euo pipefail

echo "Running database migrations..."
echo "Note: Using init.sql for initial schema. Alembic migrations will be added per-service."
echo "Done."
