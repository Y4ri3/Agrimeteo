# Décisions

**Monorepo prêt pour le multirepo.** Un dépôt, dossiers étanches (pas d'import croisé, vérifié par `scripts/check.py`), CI par dossier. Séparation possible par `git filter-repo` (voir `migration.md`).

**GitHub Actions remplace Jenkins.** Décision de l'équipe. Elle supprime les risques propres à Jenkins en conteneur (`docker.sock`, scrutation du dépôt). Les critères J-01 à J-05 du cahier se lisent ainsi : J-01 déclencheurs `push` et `pull_request` ; J-02 et J-04 `needs` et condition sur `main` ; J-03 artefacts JUnit et couverture ; J-05 secrets GitHub (seul `GITHUB_TOKEN` est utilisé). Le cahier (§8) reste à mettre à jour.

**Règles d'abord, ML à trancher.** Pas de ML dans le MVP. Un modèle exigerait une cible fiable (rendement, résultat de semis observé) ; sinon il n'a rien d'honnête à prédire. À confirmer avec M. Diop.

**Fournisseur météo : Open-Meteo.** Sans clé, historique disponible. Branché (`backend/app/providers/open_meteo.py`) : `WEATHER_PROVIDER=open_meteo` ou `?source=open_meteo`. Le défaut reste `fixture` (hors ligne, pour les tests et la CI). Fournisseur `csv` : extrait réel de l'extraction du lot 1, pour la démonstration hors ligne (dates de 2025).

**Ports du cahier.** Démonstration et développement : 3000. CI : 3100 (frontend) et 8100 (backend).
