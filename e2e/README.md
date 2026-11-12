# e2e : Playwright (lot 6)

Cible = `E2E_BASE_URL` (défaut http://localhost:3000). Les sélecteurs sont des `data-testid` du frontend.
En CI : conteneur Playwright dans le réseau Compose. En local, même commande : `sh infra/scripts/run-e2e-ci.sh` (rapport dans `reports/junit.xml`).
`analyse.spec.ts` couvre le parcours dans le navigateur, `api.spec.ts` l'API à travers nginx.
