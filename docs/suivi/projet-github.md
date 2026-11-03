# Suivi avec GitHub (Issues, Labels, Projects)
1. `sh scripts/create_labels.sh` puis `sh scripts/create_issues.sh` (une issue par ligne de `backlog.csv`).
2. Créer un **GitHub Project** (vue Board) avec les colonnes : Backlog · Prêt · En cours · En revue · Validé · Bloqué. Les issues y sont ajoutées automatiquement.
3. Une PR « Closes #n » déplace l'issue en Validé à la fusion. Étiquettes : `lot-N`, priorité, `bloque`.
