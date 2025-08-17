PYTHON := python3.11
PIP := pip3

.PHONY: install dev lint test up down clean format

install:
	pre-commit install || true

dev:
	$(PYTHON) -m venv .venv && . .venv/bin/activate && \
	$(PIP) install -U pip && \
	$(PIP) install -r services/doc-automation/requirements.txt && \
	$(PIP) install -r services/predictive/requirements.txt && \
	$(PIP) install -r libs/common/requirements.txt || true

lint:
	black --check .
	isort --check-only .
	flake8 .
	mypy --config-file pyproject.toml .

format:
	black .
	isort .

test:
	pytest -q services/doc-automation/tests
	pytest -q services/predictive/tests

up:
	docker compose -f infra/docker-compose.yml up --build

down:
	docker compose -f infra/docker-compose.yml down -v

clean:
	rm -rf .venv **/__pycache__ .mypy_cache .pytest_cache


