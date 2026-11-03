# Contribuer

**Identifiants** : `T<lot>-<nn>` (ex. T1-03), une issue par tâche. **Branche** : `feature/T1-03-slug`. **Commit** : `feat(lot1): résumé [T1-03]`. **PR** : titre `[T1-03] ...`, corps `Closes #n`, modèle fourni.
**Statuts** : Backlog → Prêt → En cours → En revue → Validé / Bloqué.

- Jamais de commit direct sur `main` ; 1 relecteur minimum (lot 6 pour le contrat, l'infra et les scripts).
- Contrat : toute modif d'API → `make -C backend openapi`, commit du JSON, mention du lot 6 dans la PR.
- Un test qui échoue n'est pas « validé ». Pas de secret dans Git (`.env` ignoré).
- Une PR = une tâche, petite. Pas de refactor opportuniste.

**Definition of Ready** : critère de test cité (ex. A-06), lot et dépendances connus, responsable nommé.
**Definition of Done** : code relu, tests/lint verts en CI, preuve jointe (`docs/preuves/`), doc mise à jour, statut changé dans le backlog.
