.PHONY: dev down test lint fmt typecheck migrate seed logs clean chat-dev dashboard-dev

dev:
	docker compose up --build -d

down:
	docker compose down -v

test:
	uv run pytest --cov -q

test-int:
	uv run pytest tests/ -m integration --cov -q

lint:
	uv run ruff check .
	uv run ruff format --check .

fmt:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy services/ libs/ agents/ --ignore-missing-imports

migrate:
	./scripts/migrate.sh

seed:
	uv run python scripts/seed.py

logs:
	docker compose logs -f

clean:
	docker compose down -v --rmi local
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true

chat-dev:
	cd apps/chat && npm run dev

dashboard-dev:
	cd apps/dashboard && npm run dev
