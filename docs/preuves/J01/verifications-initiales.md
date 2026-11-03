# Vérifications initiales (J01)
Environnement : conteneur cloud de travail (sandbox), 2026-11-02. **Pas** la machine de l'équipe, **pas** GitHub Actions.

```
$ make -C backend ci
All checks passed!
20 files already formatted

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
9 passed, 1 warning in 0.10s
$ pytest (ml)
1 passed in 0.01s
$ checks
variables manquantes dans .env.example : aucune
violations : aucune
erreurs : aucune
openapi.json à jour
$ frontend


 Test Files  1 passed (1)
      Tests  2 passed (2)

✓ built in 129ms
$ docker compose config (3 combinaisons)
OK x3 (syntaxe seulement)
```

## Exécuté avec succès
Tests backend et ml, lint, contrôles de cohérence, tests/lint/types/build frontend, e2e Playwright **local** (2/2, API uvicorn + `vite preview`, Chromium système, hors Docker), syntaxe `docker compose config` et `sh -n`.

## NON exécuté (aucune preuve)
- `docker build` / `docker compose up` : les registres d'images sont inaccessibles dans ce bac à sable.
- Workflow GitHub Actions (jamais lancé sur GitHub), `deploy-local.sh`, `rollback.sh`, `smoke-test.sh`, `run-e2e-ci.sh`.
- Fournisseur Open-Meteo, moteur de règles réel, migration multirepo.
Ces points doivent être prouvés sur une machine avec Docker (Compose >= 2.24) : première action de J2.

**Mise à jour :** Docker, déploiement, retour arrière, e2e en conteneur et migration sont prouvés dans `lots-5-6/`. Le workflow GitHub Actions reste non exécuté.
