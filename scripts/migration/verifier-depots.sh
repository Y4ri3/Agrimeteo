#!/bin/sh
# Vérifie un dépôt extrait : séparation, historique (M-01) et make ci isolé (M-02, M-03).
# Usage : verifier-depots.sh frontend|backend <dossier_du_depot>
set -eu
KIND="$1"
cd "$2"

expect_absent() {
  for P in "$@"; do
    [ ! -e "$P" ] || { echo "ÉCHEC : $P ne devrait pas être présent" >&2; exit 1; }
  done
}

case "$KIND" in
  frontend)
    expect_absent backend ml docs infra e2e frontend
    FOLLOWED=src/api.ts
    ;;
  backend)
    expect_absent frontend e2e infra
    FOLLOWED=backend/app/main.py
    ;;
  *) echo "Type inconnu : $KIND" >&2; exit 2 ;;
esac

COMMITS="$(git log --follow --oneline -- "$FOLLOWED" | wc -l)"
[ "$COMMITS" -gt 0 ] || { echo "ÉCHEC : historique perdu pour $FOLLOWED" >&2; exit 1; }
echo "M-01 $KIND : $COMMITS commit(s) suivis pour $FOLLOWED"

make setup
make ci
echo "make ci réussi pour $KIND, seul"
