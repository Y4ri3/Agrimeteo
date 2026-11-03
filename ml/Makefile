.PHONY: setup lint test ci
PY ?= python3

setup:
	$(PY) -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	mkdir -p reports
	pytest --junitxml=reports/junit.xml --cov=agrimeteo_ml --cov-report=xml:reports/coverage.xml --cov-report=term

ci: lint test
