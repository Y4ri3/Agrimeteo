# Architecture (v0, squelette)

navigateur → **nginx (frontend :8080)** → `/api/*` → **backend FastAPI :8000** → fournisseur météo (lot 1, à brancher) + moteur de règles `ml/` (lot 2).
Seul le frontend est publié. Le backend importe `ml` (paquet) ; `ml` n'importe jamais `backend` (vérifié par `scripts/check_imports.py`).
Contrat : `docs/api/openapi.json`, généré depuis le code. Trois notions toujours séparées dans les réponses : favorabilité météo, humidité du sol (indicateur modélisé), cultivabilité (non évaluée sans donnée de sol).
