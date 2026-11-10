# Décisions

**Monorepo prêt pour le multirepo.** Un dépôt, dossiers étanches (pas d'import croisé, vérifié par `scripts/check.py`), CI par dossier. Séparation possible par `git filter-repo` (voir `migration.md`).

**GitHub Actions remplace Jenkins.** Décision de l'équipe. Elle supprime les risques propres à Jenkins en conteneur (`docker.sock`, scrutation du dépôt). Les critères J-01 à J-05 du cahier se lisent ainsi : J-01 déclencheurs `push` et `pull_request` ; J-02 et J-04 `needs` et condition sur `main` ; J-03 artefacts JUnit et couverture ; J-05 secrets GitHub (seul `GITHUB_TOKEN` est utilisé). Le cahier (§8) reste à mettre à jour.

**Règles d'abord, pas de ML.** Un modèle exigerait une cible fiable (rendement, résultat de semis observé) ; sans elle, il n'a rien d'honnête à prédire. Le moteur de règles (`ml/`) est testé par des scénarios et des bornes (P-01 à P-07), pas par un taux de réussite.

**Cultures et seuils.** Arachide et mil. Les seuils viennent de la littérature (sources dans `ml/README.md`) et les profils restent `a_valider` tant que l'équipe n'a pas relu l'adaptation à une fenêtre passée ; le niveau maximal est alors « favorable sous réserve ».

**Fournisseur météo : Open-Meteo.** Sans clé, historique disponible. Branché (`backend/app/providers/open_meteo.py`) : `WEATHER_PROVIDER=open_meteo` ou `?source=open_meteo`. Le défaut reste `fixture` (hors ligne, pour les tests et la CI). Fournisseur `csv` : extrait réel de l'extraction du lot 1, pour la démonstration hors ligne (dates de 2025).

**Ports du cahier.** Démonstration et développement : 3000. CI : 3100 (frontend) et 8100 (backend).
