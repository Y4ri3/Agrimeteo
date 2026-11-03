# ADR-005 : GitHub Actions remplace Jenkins
Statut : accepté (consigne de l'enseignant ; à refléter dans le cahier, lot 5).
Pourquoi : outil imposé ; et il supprime les risques propres à Jenkins en conteneur (`docker.sock` = contrôle de l'hôte, scrutation, hôtes inaccessibles, version de Compose).
Fonctionnement : `.github/workflows/ci.yml` = jobs `checks`, `backend`, `ml`, `frontend` (parallèles) → `e2e` → sur `main` seulement : `deploy-check` → `publish` (images poussées sur GHCR, tag = commit) → `deploy`. Les rapports sont gardés en artefacts.
Déploiement : un runner GitHub ne peut pas atteindre un `localhost`. `deploy-check` rejoue donc le déploiement et le retour arrière sur le runner. Le job `deploy` lance `infra/scripts/deploy-local.sh` sur la machine cible, via un runner auto-hébergé ; il ne s'active que si la variable de dépôt `DEPLOY_SELF_HOSTED` vaut `true`, et jamais depuis une pull request. Cible réelle à confirmer avec l'enseignant (risque R-G).
Critères du cahier : J-01 = déclencheurs `push` et `pull_request` ; J-02 et J-04 = `needs` et conditions sur `main` ; J-03 = artefacts JUnit et couverture ; J-05 = GitHub Secrets (seul `GITHUB_TOKEN` est utilisé).
À activer côté GitHub (manuel, non fait) : protection de `main` (PR + relecteur + checks `checks`, `backend`, `ml`, `frontend`, `e2e` obligatoires).
