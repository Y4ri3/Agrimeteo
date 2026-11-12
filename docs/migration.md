# Migration vers le multirepo (M-01 à M-03)

La migration réelle n'est pas faite ; un essai à blanc (2026-11-02) a réussi sur un historique de test.

| Dépôt | Contenu | Pourquoi |
|---|---|---|
| `agrimeteo-frontend` | Le contenu de `frontend/`, à la racine | Il n'appelle l'API que par `/api`, sans adresse de backend à la compilation |
| `agrimeteo-backend` | `backend/`, `ml/`, `docs/api/`, chemins conservés | L'image du backend a besoin des deux, et le contrat voyage avec eux |

## Procédure
Prérequis : `git`, `git-filter-repo` (`pip install git-filter-repo`), `make`, Python et Node.

```bash
git tag pre-split                                        # dans le monorepo
sh scripts/migration/extraire-depots.sh . ../extraction  # travaille sur des clones neufs
sh scripts/migration/verifier-depots.sh frontend ../extraction/agrimeteo-frontend
sh scripts/migration/verifier-depots.sh backend  ../extraction/agrimeteo-backend
```
Le monorepo n'est pas modifié. `verifier-depots.sh` contrôle l'absence des autres modules, l'historique, puis lance `make setup` et `make ci`. Ensuite : créer les deux dépôts GitHub, y pousser les extractions, ajouter un workflow qui appelle `make setup ci`, archiver le monorepo.

## Résultat de l'essai
| Critère | Résultat |
|---|---|
| M-01 : deux dépôts depuis des clones neufs, historique conservé (`git log --follow` traverse un renommage) | Réussi |
| M-02 : `make ci` dans le dépôt frontend, sans backend | Réussi |
| M-03 : `make ci` dans le dépôt backend (avec `ml`), sans frontend | Réussi |

**Réserves.** Historique de test à refaire sur le vrai dépôt ; aucun workflow dans les dépôts extraits ; `docker-compose.yml`, e2e et scripts de déploiement n'appartiennent à aucun des deux (il faudrait un dépôt `agrimeteo-infra`, ni écrit ni testé).

**Après la séparation.** Le contrat reste dans le dépôt backend. Pour le frontend : `make gen-api OPENAPI=<chemin ou URL>`, puis committer `src/api-types.gen.ts`.
