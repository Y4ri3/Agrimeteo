# Preuves des lots 5 et 6
Environnement : poste Windows 11 de l'équipe, Docker 29.8.2, Compose 5.6.0, 2026-11-02. **Pas** GitHub Actions.

| Journal | Contenu | Où ça a tourné |
|---|---|---|
| `01-controles-ml-backend.log` | Contrôles, `make ci` de ml et backend | Conteneur `python:3.12-slim` |
| `02-frontend.log` | `make ci check-client` du frontend | Conteneur `node:22-slim` |
| `03-verify-deploy.log` | Déploiement, échec, retour automatique, retour manuel, purge | Git Bash et Docker sur le poste |
| `04-e2e-ci.log` | Contrôle des images, tests Playwright sans port publié | Git Bash et Docker sur le poste |
| `05-migration.log` | Essai à blanc de migration | Conteneurs jetables |
| `06-controles-negatifs.log` | Violations volontaires détectées par chaque contrôle Python | Conteneur `python:3.12-slim` |
| `07-deploiement-reel.log` | Déploiement de la pile principale | Git Bash et Docker sur le poste |

Sorties réelles. Seules les lignes de progression de BuildKit (`#N ...`) et les lignes vides sont retirées de `03`, `04` et `07`. Dans `05`, les lignes de progression de git et de pip sont aussi filtrées.
