.PHONY: setup lint test openapi ci
PY ?= python3

setup:
	$(PY) -m pip install -e ../ml -e ".[dev]"

lint:
	ruff check . && ruff format --check .

test:
	mkdir -p reports
	pytest --junitxml=reports/junit.xml --cov=app --cov-report=xml:reports/coverage.xml --cov-report=term

openapi:
	$(PY) -m app.export_openapi > ../docs/api/openapi.json

ci: lint test
