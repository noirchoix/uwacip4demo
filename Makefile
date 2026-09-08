.PHONY: test lint typecheck openapi compose-up compose-down

test:
	cd apps/api && pytest

lint:
	cd apps/api && ruff check .
	cd apps/web && npm run lint

typecheck:
	cd apps/api && mypy src
	cd apps/web && npm run check

openapi:
	cd apps/api && PYTHONPATH=src python ../../scripts/export_openapi.py

compose-up:
	docker compose up --build

compose-down:
	docker compose down
