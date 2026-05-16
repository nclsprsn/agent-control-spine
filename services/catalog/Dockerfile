FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY libs/spine-common ./libs/spine-common
COPY services/catalog ./services/catalog
RUN uv sync --frozen --no-dev --no-editable --package catalog

FROM python:3.14-slim-bookworm
RUN useradd -u 1000 -m -s /usr/sbin/nologin app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8082
CMD ["uvicorn", "catalog.main:app", "--host", "0.0.0.0", "--port", "8082"]
