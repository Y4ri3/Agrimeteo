#!/bin/sh
# Revient à la version précédente, sans rien reconstruire : ses images doivent encore exister (C-07).
set -eu
cd "$(dirname "$0")/../.."

STATE="${DEPLOY_STATE_DIR:-infra/deploy}"
TIMEOUT="${DEPLOY_TIMEOUT:-90}"
PORT="${FRONTEND_PORT:-$(sed -n 's/^FRONTEND_PORT=//p' .env | tr -d '\r')}"

[ -f "$STATE/previous.tag" ] || { echo "Aucune version précédente connue" >&2; exit 1; }
PREVIOUS="$(cat "$STATE/previous.tag")"
for SERVICE in backend frontend; do
  docker image inspect "agrimeteo-$SERVICE:$PREVIOUS" >/dev/null 2>&1 \
    || { echo "Image absente : agrimeteo-$SERVICE:$PREVIOUS" >&2; exit 1; }
done

IMAGE_TAG="$PREVIOUS" docker compose up -d --no-build --wait --wait-timeout "$TIMEOUT"
sh infra/scripts/smoke-test.sh "http://localhost:${PORT:-3000}"
cp "$STATE/previous.tag" "$STATE/current.tag"
echo "Retour arrière réussi : $PREVIOUS"
