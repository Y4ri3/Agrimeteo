# Rapport d'essai de migration

**Résultat : l'extraction de deux dépôts fonctionne. M-01, M-02 et M-03 sont passés, sur un historique de test.**

Date : 2026-11-02. Journal complet : `docs/preuves/J01/lots-5-6/05-migration.log`.

## Résultats
| Critère | Vérification | Résultat |
|---|---|---|
| M-01 | Deux dépôts produits depuis des clones neufs, monorepo inchangé (même commit avant et après) | Réussi |
| M-01 | `git log --follow` sur `src/api.ts` remonte au-delà d'un renommage (2 commits) | Réussi |
| M-02 | `make setup` puis `make ci` dans le dépôt frontend, sans backend dans le conteneur | Réussi : lint, types, 2 tests, build |
| M-03 | `make setup` puis `make ci` dans le dépôt backend, sans frontend | Réussi : lint, 10 tests, contrat à jour |
| En plus | `docker build` de chaque dépôt extrait | Réussi : images non root |

## Méthode
Chaque étape a tourné dans un conteneur Linux jetable : `python:3.12-slim` pour l'extraction et le backend, `node:22-slim` pour le frontend. Chaque dépôt a été vérifié sans les dossiers de l'autre : le script contrôle leur absence avant de lancer `make ci`.

## Réserves
- **Historique de test.** Le dossier de travail n'étant pas un dépôt Git, l'essai a créé un monorepo temporaire de 4 commits, dont un renommage. L'essai reste à refaire sur le vrai dépôt, dont l'historique sera plus riche.
- **Aucun workflow dans les dépôts extraits.** `make ci` y fonctionne, mais aucun pipeline ne les lance encore : le workflow est à la racine du monorepo.
- **Pas de test de la pile assemblée après séparation.** Aucun dépôt ne contient `docker-compose.yml` ni les tests e2e (voir `docs/migration-multirepo.md`).

## Problèmes trouvés par l'essai
| Problème | Correction |
|---|---|
| `make ci` absent de `frontend` et de `ml`, et à la racine | Cibles ajoutées |
| Le dépôt backend n'avait ni `make ci` à la racine ni contrôle du contrat | `scripts/migration/backend.Makefile` devient son Makefile racine, et `check_openapi.py` part avec lui |
| Le dépôt frontend perdait le `.gitignore` racine | `frontend/.gitignore` ajouté |
| La documentation précédente exigeait de publier `ml` comme paquet | Inutile : `backend` et `ml` restent ensemble, comme le prévoit le cahier |
