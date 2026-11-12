# Décisions

**Monorepo prêt pour le multirepo.** Un dépôt, dossiers étanches (pas d'import croisé, vérifié par `scripts/check.py`), CI par dossier. Séparation possible par `git filter-repo` (voir `migration.md`).

**GitHub Actions remplace Jenkins.** Décision de l'équipe. Elle supprime les risques propres à Jenkins en conteneur (`docker.sock`, scrutation du dépôt). Les critères J-01 à J-05 du cahier se lisent ainsi : J-01 déclencheurs `push` et `pull_request` ; J-02 et J-04 `needs` et condition sur `main` ; J-03 artefacts JUnit et couverture ; J-05 secrets GitHub (seul `GITHUB_TOKEN` est utilisé). Le cahier (§8) reste à mettre à jour.

**Règles, pas de machine learning (décision définitive).** Un modèle exigerait une cible fiable (rendement, résultat de semis observé) ; sans elle, il n'a rien d'honnête à prédire. Le moteur de règles (`ml/`) est testé par des scénarios et des bornes (P-01 à P-07), pas par un taux de réussite.

**Cultures et seuils.** Tomate, riz, arachide et mil : les profils du notebook définitif du lot 2 (`devoir_devops.ipynb`), repris tels quels dans `ml/rules/`. Leurs seuils viennent de références générales (FAO EcoCrop, IRRI) dont plusieurs ne sont pas des références précises : les profils restent `a_valider` et le niveau maximal est « favorable sous réserve ». Pour passer un profil à `valide_par_source`, citer pour chaque seuil une source identifiable (ouvrage, page, valeur).

**Déploiement sur un serveur avec nginx global.** Le nginx du serveur reste le seul point d'entrée (domaine, HTTPS) et relaie vers le conteneur frontend, publié sur `127.0.0.1:3000` seulement. La CI copie le code par SSH (rsync) et lance `deploy-local.sh` sur le serveur, qui garde les versions pour le retour arrière (C-06, C-07). Pas de registre d'images : les images sont construites sur le serveur.

**Ports du cahier.** Démonstration et développement : 3000. CI : 3100 (frontend) et 8100 (backend).
