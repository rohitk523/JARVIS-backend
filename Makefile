.PHONY: install test lint dev-api dev-agent

install:
	poetry install

test:
	poetry run pytest -v

lint:
	poetry run ruff check .
	poetry run ruff format --check .

dev-api:
	poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

dev-agent:
	poetry run python -m agent.main dev
