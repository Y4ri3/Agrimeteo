# Devient le Makefile racine du dépôt agrimeteo-backend après extraction (voir extraire-depots.sh).
.PHONY: setup ci
PY ?= python3

setup:
	$(MAKE) -C ml setup PY=$(PY)
	$(MAKE) -C backend setup PY=$(PY)

ci:
	$(MAKE) -C ml ci
	$(MAKE) -C backend ci
	$(PY) scripts/check_openapi.py
