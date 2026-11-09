# Contribuer

Conventions du cahier des charges (§4.3) :

- `main` est protégée : on ne pousse jamais dessus directement. Toute modification passe par une pull request avec au moins une relecture.
- Une branche par sujet, nommée `feature/lot-sujet` (exemple : `feature/lot3-geocode`). Une branche dure moins d'un jour ; on ne fusionne que si la CI est verte.
- Messages de commit courts, au format `type: message` (`feat`, `fix`, `docs`, `test`, `ci`).
- Contrat : toute modif d'API → `make -C backend openapi`, `make -C frontend gen-api`, commit des deux fichiers, mention du lot 6 dans la PR.
- Un test qui échoue n'est pas « validé ». Pas de secret dans Git (`.env` ignoré).
