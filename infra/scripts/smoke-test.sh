#!/bin/sh
# Usage: smoke-test.sh [base_url]  -- vérifie le front, l'API derrière nginx et une analyse complète (C-06).
set -eu
BASE="${1:-http://localhost:3000}"

curl -fsS --max-time 10 "$BASE/" >/dev/null
echo "front OK"

CROPS="$(curl -fsS --max-time 10 "$BASE/api/v1/crops")"
CROP_ID="$(printf '%s' "$CROPS" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p')"
[ -n "$CROP_ID" ] || { echo "aucun profil de culture renvoyé par l'API" >&2; exit 1; }
echo "api OK (via nginx)"

RESULT="$(curl -fsS --max-time 30 -X POST "$BASE/api/v1/predictions" \
  -H 'Content-Type: application/json' \
  -d "{\"crop_id\":\"$CROP_ID\",\"location\":{\"latitude\":14.69,\"longitude\":-17.44}}")"
case "$RESULT" in
  *'"meteorological_favorability"'*) echo "analyse OK ($CROP_ID)" ;;
  *) echo "réponse d'analyse inattendue" >&2; exit 1 ;;
esac
