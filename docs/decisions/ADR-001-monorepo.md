# ADR-001 : monorepo prêt pour le multirepo
Statut : accepté. Un dépôt, dossiers étanches (pas d'import croisé, vérifié par script), CI par dossier. Découpage possible via `git filter-repo` (voir `migration-multirepo.md`, non exécutée). Coût : un seul workflow à garder lisible (jobs séparés par dossier).
