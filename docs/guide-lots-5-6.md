# Guide des lots 5 et 6

Ce guide explique ce qui a été mis en place pour le lot 5 (DevOps et déploiement) et le lot 6 (architecture et intégration), comment s'en servir et ce qu'il reste à faire. Il suppose de connaître Docker et Git, mais pas ce dépôt.

## L'essentiel

- La pile démarre, se déploie et revient en arrière sur Docker. Tout cela a été exécuté, les journaux sont dans [`docs/preuves/J01/lots-5-6/`](preuves/J01/lots-5-6/).
- Le découpage en deux dépôts fonctionne : chaque dépôt extrait passe `make ci` seul.
- **Le workflow GitHub Actions n'a encore jamais tourné sur GitHub**, car le dépôt n'y est pas encore poussé. Les critères J-01 à J-05 restent donc à prouver (voir [À faire](#à-faire)).
- L'application répond toujours avec des **données factices** : les lots 1 à 4 ne sont pas branchés.

## Démarrer le projet

Prérequis : Docker Desktop lancé et Compose 2.24 ou plus récent. Sous Windows, utilisez **Git Bash** pour les commandes `sh`.

```bash
cp .env.example .env
sh infra/scripts/deploy-local.sh
```

Ouvrez ensuite <http://localhost:8080>. Le script construit les images, démarre la pile et lance le smoke test.

Pour arrêter : `docker compose down`.

## Les commandes utiles

| Besoin | Avec make | Sans make (Git Bash) |
|---|---|---|
| Déployer une version | `make deploy` | `sh infra/scripts/deploy-local.sh` |
| Revenir à la version précédente | `make rollback` | `sh infra/scripts/rollback.sh` |
| Vérifier la pile en service | `make smoke` | `sh infra/scripts/smoke-test.sh` |
| Lancer les tests e2e en conteneur | `make e2e` | `sh infra/scripts/run-e2e-ci.sh` |
| Rejouer le scénario déploiement et retour arrière | `make verify-deploy` | `sh infra/scripts/verify-deploy.sh` |
| Installer les dépendances | `make setup` | voir le README de chaque module |
| Tout vérifier sans Docker (comme la CI) | `make ci` | voir le workflow `.github/workflows/ci.yml` |

`make` n'est pas installé d'office sous Windows : `winget install ezwinports.make` l'ajoute. Les commandes `make` de ce guide ont été exécutées dans des conteneurs Linux, pas directement sous Windows.

Les tests e2e et `verify-deploy` utilisent chacun leur propre projet Compose. Ils ne touchent donc pas à la pile en service.

## Lot 5 : construire, tester, déployer

### Le pipeline

Le cahier des charges prévoit Jenkins, mais [ADR-005](decisions/ADR-005-github-actions.md) le remplace par GitHub Actions, sur consigne de l'enseignant. Les six étapes du cahier sont conservées :

```text
  checks ──┐
  backend ─┤
  ml ──────┼──> e2e ──> deploy-check ──> publish ──> deploy
  frontend ┘            └──── main seulement ─────┘  (si runner auto-hébergé)
```

| Étape du cahier | Job | Ce qu'il fait |
|---|---|---|
| 1. Récupération | tous | `actions/checkout`, à chaque push sur `main` et à chaque pull request |
| 2. Qualité statique | `checks` et les jobs de module | ruff, ESLint, tsc, imports, `.env.example`, secrets, contrat, client généré |
| 3. Tests | `backend`, `ml`, `frontend` | pytest et Vitest en parallèle, rapports JUnit gardés en artefacts |
| 4. Build des images | `e2e` | construit les images et contrôle qu'elles sont non root et sans secret |
| 5. Intégration | `e2e` | pile avec le fournisseur fixture, sans port publié, puis Playwright |
| 6. Déploiement | `deploy-check`, `publish`, `deploy` | voir ci-dessous |

Si un job échoue, ceux qui en dépendent ne partent pas : rien n'est publié ni déployé.

Un runner hébergé par GitHub ne peut pas atteindre une machine locale. Le déploiement se fait donc en trois temps :

1. `deploy-check` rejoue déploiement, échec et retour arrière sur le runner.
2. `publish` pousse les images sur GHCR, avec le commit comme tag.
3. `deploy` lance le script sur la machine cible. Ce job ne s'active que si un runner auto-hébergé existe et que la variable de dépôt `DEPLOY_SELF_HOSTED` vaut `true`.

### Le déploiement et le retour arrière

`deploy-local.sh` enchaîne : build, `docker compose up --wait`, puis smoke test.

- **Si tout passe** : la version est notée dans `infra/deploy/current.tag` et l'ancienne dans `previous.tag`. Les images trop anciennes sont supprimées. Le script garde la version en service, la précédente et les 3 plus récentes (`IMAGE_KEEP`).
- **Si le démarrage ou le smoke test échoue** : l'ancienne version est relancée, les images ratées sont supprimées et le script renvoie une erreur.
- **Si le build échoue** : rien n'a bougé, l'ancienne version continue de tourner.

`rollback.sh` relance la version de `previous.tag` sans rien reconstruire. Il s'arrête si les images n'existent plus, au lieu de reconstruire le code actuel sous l'ancien tag.

Détails d'exploitation : [`docs/exploitation.md`](exploitation.md).

### Les défauts corrigés

| Défaut trouvé | Conséquence | Correction |
|---|---|---|
| Contrat généré avec un Python plus récent que celui de la CI : le libellé de l'erreur 422 dépend de la version de Python | La CI aurait échoué dès son premier lancement | Libellé fixé dans `routes.py`, contrôle vérifié en Python 3.12 et 3.14 |
| `curl ... && echo` sous `set -e` dans le smoke test | Un frontend en panne pouvait passer inaperçu | Commandes séparées |
| Smoke test sans analyse | C-06 non couvert | Il lance maintenant une vraie analyse |
| Version notée avant de savoir si le déploiement réussit, et aucun retour automatique | Une version cassée restait en service et devenait la « version en service » | Écriture après réussite, retour automatique |
| Même tag `local` pour toutes les versions | Retour arrière impossible | Tag `<build>-<commit>` |
| Tests e2e dans le même projet Compose que la pile déployée | Ils écrasaient la pile en service | Projet `agrimeteo-ci` |
| Un nouveau push sur `main` annulait le workflow en cours | Un déploiement pouvait être coupé en plein milieu | Annulation réservée aux pull requests |
| `check_*.py` sans encodage déclaré | Risque d'erreur sous Windows | `encoding="utf-8"` |

## Lot 6 : garder l'ensemble cohérent

### Le contrat d'API et le client généré

`docs/api/openapi.json` est généré depuis le code. Deux contrôles empêchent les dérives :

- **Côté backend** : `scripts/check_openapi.py` échoue si le fichier ne correspond plus à l'API (A-02).
- **Côté frontend** : les types de [`frontend/src/api.ts`](../frontend/src/api.ts) viennent de `src/api-types.gen.ts`, généré depuis le contrat. Si un champ utilisé disparaît, la compilation casse (I-01). `make check-client` échoue si le fichier généré n'est plus à jour.

Pour modifier l'API : `make -C backend openapi`, puis `make -C frontend gen-api`, puis committer les deux fichiers et mentionner le lot 6 dans la PR.

`openapi-typescript` n'est pas dans `package.json` car il exige TypeScript 5 et le projet est en TypeScript 6. Sa version est fixée dans `frontend/Makefile`, et `make ci` n'en a pas besoin puisque le fichier généré est committé.

### Les contrôles automatiques

| Script | Critère | Ce qu'il refuse |
|---|---|---|
| `scripts/check_imports.py` | I-04 | Les imports interdits du cahier (4.2), frontend compris |
| `scripts/check_env_example.py` | C-05 | Une variable lue par `backend/app` ou `ml/src` et absente de `.env.example` |
| `scripts/check_secrets.py` | C-04 | Clés, jetons, valeurs sensibles, ou `.env` suivi par Git |
| `scripts/check_openapi.py` | A-02 | Un contrat différent de l'API réelle |
| `infra/scripts/check-images.sh` | C-03, C-04 | Une image en root, un secret dans `docker history`, un `.env` dans l'image |

Les contrôles Python ont été testés avec des violations volontaires, et tous les ont détectées ([journal](preuves/J01/lots-5-6/06-controles-negatifs.log)). `check-images.sh` n'a été exécuté que sur des images conformes.

`check_secrets.py` repère des motifs connus. Il réduit le risque mais ne garantit pas l'absence de tout secret.

### Les tests de bout en bout

Ils tournent dans un conteneur Playwright, sur le réseau Compose, sans port publié ([ADR-002](decisions/ADR-002-ci-sans-ports.md)).

| Test | Critère | Vérifie |
|---|---|---|
| `analyse.spec.ts` : parcours nominal | I-02, A-06 | Analyse lancée, trois notions séparées, confiance affichée |
| `analyse.spec.ts` : source indisponible | I-03 | Message d'erreur, puis nouvelle analyse réussie |
| `analyse.spec.ts` : limites affichées | F7, FE-03 | **En attente** : affichage des `limits` à faire côté frontend (lot 4) |
| `api.spec.ts` : smoke | C-06 | Frontend, relais nginx, analyse complète |
| `api.spec.ts` : erreur | A-03 | Format d'erreur commun, sans trace interne |

Tant que le lot 1 n'a pas de vrai fournisseur, la panne de I-03 est simulée dans le navigateur. Ce test devra passer par un fournisseur réellement indisponible une fois celui-ci branché.

### La migration vers deux dépôts

La procédure est dans [`docs/migration-multirepo.md`](migration-multirepo.md) et le résultat de l'essai dans [`docs/suivi/rapport-essai-migration.md`](suivi/rapport-essai-migration.md).

## Où en sont les critères

| Critère | État | Preuve ou réserve |
|---|---|---|
| C-01 build | Prouvé | Depuis le dossier de travail et depuis les dépôts extraits, pas encore depuis un vrai clone GitHub |
| C-02 services healthy | Prouvé | `07-deploiement-reel.log` |
| C-03 non root | Prouvé | `04-e2e-ci.log` |
| C-04 aucun secret | Prouvé | `06-controles-negatifs.log`, `04-e2e-ci.log`. Les journaux de build GitHub restent à vérifier |
| C-05 `.env.example` | Prouvé | `01-controles-ml-backend.log` |
| C-06 smoke après déploiement | Prouvé | `03-verify-deploy.log`, `07-deploiement-reel.log` |
| C-07 retour arrière | Prouvé | `03-verify-deploy.log`, avec des versions au contenu identique : le test contrôle le tag en service |
| J-01 pipeline à chaque push | **Non prouvé** | Workflow validé par actionlint uniquement |
| J-02 test cassé, pas de déploiement | **Non prouvé** | À démontrer sur GitHub |
| J-03 rapports consultables | **Non prouvé** | Rapports produits en local, artefacts à voir sur GitHub |
| J-04 déploiement depuis `main` seulement | **Non prouvé** | Conditions écrites dans le workflow, à voir sur GitHub |
| J-05 secrets | **Non prouvé** | Aucun secret requis à ce stade, sauf le `GITHUB_TOKEN` fourni par GitHub |
| A-02 contrat à jour | Prouvé | `01-controles-ml-backend.log`, `06-controles-negatifs.log` |
| I-01 client généré | Prouvé | `02-frontend.log` |
| I-02 parcours nominal | Prouvé | `04-e2e-ci.log`, sur données factices |
| I-03 scénario d'erreur | Partiel | `04-e2e-ci.log`, panne simulée dans le navigateur |
| I-04 imports | Prouvé | `06-controles-negatifs.log` |
| M-01 extraction | Prouvé | `05-migration.log`, sur un historique de test |
| M-02, M-03 `make ci` isolé | Prouvé | `05-migration.log` |

Ces journaux viennent d'une seule machine : le poste Windows de l'équipe, avec Docker 29.8.2 et Compose 5.6.0, le 2026-11-02.

## À faire

**Pour prouver J-01 à J-05** (lot 5) :

1. Créer le dépôt GitHub : le dossier actuel n'est pas encore un dépôt Git.
2. Pousser le code et vérifier que le workflow passe au vert dans l'onglet Actions.
3. Protéger `main` : pull request, un relecteur, et les checks `checks`, `backend`, `ml`, `frontend`, `e2e` obligatoires.
4. Sur une branche, casser un test : le workflow doit échouer et rien ne doit être déployé (J-02). Copier le lien du run dans `docs/preuves/`.
5. Trancher avec l'enseignant la machine de démonstration (risque R-G). Si un runner auto-hébergé est retenu, l'installer sur une machine Linux et mettre `DEPLOY_SELF_HOSTED` à `true`.

**Pour l'équipe** :

- Remplacer les noms provisoires de `.github/CODEOWNERS` par les vrais identifiants (lots 5 et 6).
- Lot 4 : afficher les limites avec `data-testid="limits"`, puis retirer `test.fixme` dans `analyse.spec.ts` (AN-01).
- Lancer l'essai de migration sur le vrai dépôt : il a été fait sur un historique de test.

## Écarts avec le cahier des charges

| Cahier | Dépôt | Raison |
|---|---|---|
| Jenkins et `Jenkinsfile` | GitHub Actions | [ADR-005](decisions/ADR-005-github-actions.md), consigne de l'enseignant |
| Ports de test 8100 et 3100 en intégration | Aucun port publié | [ADR-002](decisions/ADR-002-ci-sans-ports.md) |
| Frontend sur le port 3000 | Port 8080 | Choix déjà présent dans le squelette, réglable avec `FRONTEND_PORT` |
| Filtre `backend/`, `ml/`, `docs/api/` | S'y ajoutent `check_openapi.py`, un Makefile racine et les fichiers de configuration | Nécessaires pour que `make ci` et le contrôle du contrat marchent seuls |

## Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `failed to connect to the docker API` | Docker Desktop est arrêté | Le lancer et attendre qu'il soit prêt |
| `port is already allocated` | Le port 8080 est pris | Changer `FRONTEND_PORT` dans `.env` |
| `Aucune version précédente connue` | Un seul déploiement a eu lieu | Déployer une seconde version d'abord |
| `Image absente` au retour arrière | L'image a été supprimée | Redéployer ce commit avec `IMAGE_TAG=<tag>` |
| `openapi.json DIVERGE` | L'API a changé sans régénérer le contrat | `make -C backend openapi`, puis `make -C frontend gen-api` |
| `cmp` échoue dans `check-client` | Types générés périmés | `make -C frontend gen-api` |
| `http://localhost:8080/health` renvoie du HTML | Comportement normal : nginx ne relaie que `/api/` | Utiliser `/api/v1/crops`, ou `make dev` pour accéder au backend sur le port 8000 |
