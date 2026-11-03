# frontend : React + Vite (lot 4)

Squelette : une page qui appelle `/api/v1/crops` et `/api/v1/predictions`. Les `data-testid` sont le contrat avec les tests e2e : ne pas les renommer sans prévenir le lot 6.

```bash
make setup && npm run dev   # proxy /api -> localhost:8000
make ci                     # lint, types, tests (rapport dans reports/), build
make gen-api                # régénère src/api-types.gen.ts depuis le contrat (à committer)
```
Ne pas modifier `src/api-types.gen.ts` à la main : `make check-client` échoue s'il diverge du contrat.
