FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY libs/spine-common ./libs/spine-common
COPY services/registry ./services/registry
RUN uv sync --frozen --no-dev --no-editable --package registry

FROM python:3.14-slim-bookworm
RUN apt-get update && apt-get upgrade -y --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN useradd -u 1000 -m -s /usr/sbin/nologin app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8081
CMD ["uvicorn", "registry.main:app", "--host", "0.0.0.0", "--port", "8081"]
