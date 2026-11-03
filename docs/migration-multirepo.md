# Migration vers le multirepo

Essai à blanc réussi : voir `docs/suivi/rapport-essai-migration.md`. La migration réelle n'est pas faite.

## Ce qu'on obtient
| Dépôt | Contenu | Pourquoi |
|---|---|---|
| `agrimeteo-frontend` | Le contenu de `frontend/`, à la racine | Il n'appelle l'API que par `/api`, sans adresse de backend à la compilation |
| `agrimeteo-backend` | `backend/`, `ml/`, `docs/api/`, chemins conservés | L'image du backend a besoin des deux, et le contrat voyage avec eux |

## Procédure
Prérequis : `git` et `git-filter-repo` (`pip install git-filter-repo`), plus `make`, Python et Node pour la vérification.

```bash
git tag pre-split                                        # dans le monorepo
sh scripts/migration/extraire-depots.sh . ../extraction  # travaille sur des clones neufs
sh scripts/migration/verifier-depots.sh frontend ../extraction/agrimeteo-frontend
sh scripts/migration/verifier-depots.sh backend  ../extraction/agrimeteo-backend
```
Le monorepo n'est pas modifié par ces scripts. `verifier-depots.sh` contrôle l'absence des autres modules, l'historique, puis lance `make setup` et `make ci`.

Ensuite, si la vérification passe :
1. Créer les deux dépôts sur GitHub et y pousser les extractions.
2. Ajouter un workflow à chaque dépôt : il suffit d'appeler `make setup ci`.
3. Archiver le monorepo en lecture seule.

## Après la séparation
- **Contrat** : `docs/api/openapi.json` reste dans le dépôt backend. Pour mettre à jour le frontend : `make gen-api OPENAPI=<chemin ou URL du contrat>`, puis committer `src/api-types.gen.ts`.
- **Assemblage** : le `docker-compose.yml`, les tests e2e et les scripts de déploiement restent dans le monorepo. Ils ne sont dans aucun des deux dépôts extraits. Il faudra les placer dans un troisième dépôt `agrimeteo-infra` et lui faire construire les images depuis les deux autres : cette partie n'est ni écrite ni testée.
