# AgriMétéo

Application d'aide à la décision agricole (projet DevOps, DIT L3). Monorepo : `backend/` (API), `ml/` (règles), `frontend/`, `e2e/`, `infra/`, `scripts/`, `docs/`.

## Démarrer (sans Docker)
```bash
python3 -m venv .venv && . .venv/bin/activate
make -C backend setup && uvicorn app.main:app --app-dir backend --reload   # API :8000/docs
cd frontend && npm ci && npm run dev                                      # UI :5173
```
## Démarrer (Docker, Compose >= 2.24)
```bash
cp .env.example .env && make up && make smoke      # http://localhost:8080
```
Sous Windows sans `make`, depuis Git Bash : `sh infra/scripts/deploy-local.sh`.
## État honnête
Squelette : l'API répond avec des **données factices** (`backend/app/services/stub.py`). Rien d'agronomique n'est réel.
CI : GitHub Actions (`.github/workflows/ci.yml`), **pas encore exécutée sur GitHub**. Suivi : Issues + Labels + Projects (`docs/suivi/projet-github.md`).
Déploiement, retour arrière, e2e et essai de migration : exécutés en local, voir **`docs/guide-lots-5-6.md`**.
Preuves d'exécution : `docs/preuves/`. Exploitation : `docs/exploitation.md`. Conventions : `CONTRIBUTING.md`. Décisions : `docs/decisions/`.
