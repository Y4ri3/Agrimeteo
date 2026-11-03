.PHONY: setup lint test build ci gen-api check-client
OPENAPI ?= ../docs/api/openapi.json
# Hors de package.json : l'outil exige TypeScript 5, le projet est en TypeScript 6.
GEN_CLIENT = npx --yes openapi-typescript@7.13.0

setup:
	npm ci
lint:
	npm run lint && npm run typecheck
test:
	npm test -- --reporter=default --reporter=junit --outputFile.junit=reports/junit.xml
build:
	npm run build
ci: lint test build
# Régénère les types depuis le contrat. Le fichier produit est committé : `make ci` n'a pas besoin du backend.
gen-api:
	$(GEN_CLIENT) $(OPENAPI) -o src/api-types.gen.ts
check-client:
	mkdir -p reports
	$(GEN_CLIENT) $(OPENAPI) -o reports/api-types.check.ts
	cmp src/api-types.gen.ts reports/api-types.check.ts
