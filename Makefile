.PHONY: setup check ci up down dev smoke e2e deploy rollback
setup:
	$(MAKE) -C ml setup
	$(MAKE) -C backend setup
	$(MAKE) -C frontend setup
check:
	python3 scripts/check.py && python3 scripts/check_openapi.py
ci: check
	$(MAKE) -C ml ci
	$(MAKE) -C backend ci
	$(MAKE) -C frontend ci check-client
up:
	docker compose up -d --build --wait
dev:
	docker compose -f docker-compose.yml -f infra/compose/docker-compose.dev.yml up -d --build --wait
down:
	docker compose down
smoke:
	sh infra/scripts/smoke-test.sh
e2e:
	sh infra/scripts/run-e2e-ci.sh
deploy:
	sh infra/scripts/deploy-local.sh
rollback:
	sh infra/scripts/rollback.sh
