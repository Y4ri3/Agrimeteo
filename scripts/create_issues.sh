#!/bin/sh
# Crée les issues GitHub depuis docs/suivi/backlog.csv (nécessite `gh auth login`). Non exécuté tant que le dépôt n'existe pas.
set -eu
tail -n +2 docs/suivi/backlog.csv | while IFS=';' read -r id lot titre prio sprint; do
  gh issue create --title "[$id] $titre" --label "lot-$lot,$prio" --body "Lot $lot · Sprint $sprint. Voir docs/suivi/definition-of-ready-done.md"
done
