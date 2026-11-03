# Anomalies

| ID | Description | Gravité | Statut |
|---|---|---|---|
| AN-01 | L'application n'affiche pas les limites renvoyées par l'API (`limits`). Le cahier les classe parmi ce qu'il ne faut jamais abandonner (F7, FE-03). Lot 4 : les afficher avec `data-testid="limits"`, puis activer le test `test.fixme` de `e2e/tests/analyse.spec.ts`. | Haute | Ouverte |
| AN-02 | `docs/api/openapi.json` dépendait de la version de Python (libellé de l'erreur 422) : la CI en 3.12 aurait échoué. | Haute | Corrigée |
| AN-03 | `smoke-test.sh` pouvait ignorer une panne du frontend, et ne lançait aucune analyse. | Moyenne | Corrigée |
| AN-04 | `deploy-local.sh` enregistrait la version avant le résultat, sans retour automatique ; tag `local` unique. | Haute | Corrigée |
| AN-05 | `npm audit` signale 11 vulnérabilités modérées dans les dépendances de développement du frontend (dont `minimatch`). Aucune en production (`npm audit --omit=dev`). Lot 4 : à mettre à jour. | Faible | Ouverte |
