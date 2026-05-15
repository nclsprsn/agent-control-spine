FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY libs/spine-common ./libs/spine-common
COPY services/observer ./services/observer
RUN uv sync --frozen --no-dev --package observer

FROM python:3.14-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8083
CMD ["uvicorn", "observer.main:app", "--host", "0.0.0.0", "--port", "8083"]
