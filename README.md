# AgriMétéo

Application web qui estime si les conditions météo sont favorables à la mise en culture (projet DevOps, DIT L3). Cahier des charges : `AgriMeteo_Cahier_des_charges.docx`.

Monorepo : `backend/` (API FastAPI) · `ml/` (règles) · `frontend/` (React) · `e2e/` · `infra/` · `scripts/` · `docs/`.

navigateur → **nginx (frontend)** → `/api/*` → **backend FastAPI** (interne) → fournisseur météo + moteur de règles `ml/`.
Seul le frontend est publié. `ml` n'importe jamais `backend` (vérifié par `scripts/check.py`). Le contrat est `docs/api/openapi.json`, généré depuis le code. Trois notions toujours séparées : favorabilité météo, humidité du sol (indicateur modélisé), cultivabilité (non évaluée).

## Démarrer
```bash
cp .env.example .env && make up && make smoke      # http://localhost:3000
```
Sans Docker :
```bash
python3 -m venv .venv && . .venv/bin/activate
make -C backend setup && uvicorn app.main:app --app-dir backend --reload   # API :8000/docs
cd frontend && npm ci && npm run dev                                      # UI :5173
```
`make ci` lance tous les contrôles (sans Docker). Sous Windows sans `make` : `sh infra/scripts/deploy-local.sh` depuis Git Bash.

## État
Trois fournisseurs : `open_meteo` (données réelles, `WEATHER_PROVIDER=open_meteo`), `csv` (extrait réel hors ligne) et `fixture` (factice, défaut des tests et de la CI). Le moteur de décision est provisoire (toujours « indéterminé ») : le moteur de règles et les seuils relèvent du lot 2. La CI GitHub Actions n'a pas encore tourné sur GitHub.

Voir aussi : `docs/exploitation.md` (pipeline, déploiement, retour arrière), `docs/decisions.md`, `docs/migration.md`, `CONTRIBUTING.md`.
