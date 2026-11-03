#!/bin/sh
# Crée les étiquettes GitHub (lots, priorités, statuts). Nécessite `gh auth login`. Non exécuté.
set -eu
for n in 1 2 3 4 5 6; do gh label create "lot-$n" --color 1f6feb --force; done
for p in haute moyenne basse; do gh label create "$p" --color d29922 --force; done
for s in bloque en-revue; do gh label create "$s" --color d73a49 --force; done
