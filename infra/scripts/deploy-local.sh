#!/bin/sh
# Déploie une nouvelle version : build, démarrage, smoke test. En cas d'échec, relance la version précédente.
# Variables : IMAGE_TAG (défaut <build>-<commit>), DEPLOY_STATE_DIR (défaut infra/deploy),
# DEPLOY_TIMEOUT (secondes, défaut 90), IMAGE_KEEP (anciennes versions gardées, défaut 3), SMOKE_BASE_URL.
set -eu
cd "$(dirname "$0")/../.."
[ -f .env ] || cp .env.example .env

STATE="${DEPLOY_STATE_DIR:-infra/deploy}"
TIMEOUT="${DEPLOY_TIMEOUT:-90}"
KEEP="${IMAGE_KEEP:-3}"
PORT="${FRONTEND_PORT:-$(sed -n 's/^FRONTEND_PORT=//p' .env | tr -d '\r')}"
URL="http://localhost:${PORT:-3000}"
mkdir -p "$STATE"

if [ -z "${IMAGE_TAG:-}" ]; then
  COMMIT="$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M%S)"
  IMAGE_TAG="${BUILD_NUMBER:-${GITHUB_RUN_NUMBER:-manual}}-$COMMIT"
fi
export IMAGE_TAG
CURRENT="$(cat "$STATE/current.tag" 2>/dev/null || true)"

remove_images() {
  docker image rm "agrimeteo-backend:$1" "agrimeteo-frontend:$1" >/dev/null 2>&1 || true
}

# Garde la version en service, la précédente et les IMAGE_KEEP plus récentes ; supprime les autres.
prune_old_versions() {
  { grep -vxF "$IMAGE_TAG" "$STATE/history" 2>/dev/null || true; echo "$IMAGE_TAG"; } >"$STATE/history.tmp"
  PREVIOUS="$(cat "$STATE/previous.tag" 2>/dev/null || true)"
  KEPT=0
  : >"$STATE/history.new"
  for TAG in $(sed -n '1!G;h;$p' "$STATE/history.tmp"); do
    if [ "$TAG" != "$IMAGE_TAG" ] && [ "$TAG" != "$PREVIOUS" ]; then
      KEPT=$((KEPT + 1))
      if [ "$KEPT" -gt "$KEEP" ]; then
        echo "Suppression de l'ancienne version : $TAG"
        remove_images "$TAG"
        continue
      fi
    fi
    echo "$TAG" >>"$STATE/history.new"
  done
  sed -n '1!G;h;$p' "$STATE/history.new" >"$STATE/history"
  rm -f "$STATE/history.tmp" "$STATE/history.new"
}

echo "Déploiement de la version $IMAGE_TAG (version en service : ${CURRENT:-aucune})"
docker compose build

if docker compose up -d --wait --wait-timeout "$TIMEOUT" && sh infra/scripts/smoke-test.sh "${SMOKE_BASE_URL:-$URL}"; then
  if [ -n "$CURRENT" ] && [ "$CURRENT" != "$IMAGE_TAG" ]; then
    echo "$CURRENT" >"$STATE/previous.tag"
  fi
  echo "$IMAGE_TAG" >"$STATE/current.tag"
  prune_old_versions
  echo "Déploiement réussi : $IMAGE_TAG"
  exit 0
fi

echo "Échec du déploiement de $IMAGE_TAG" >&2
if [ -n "$CURRENT" ] && [ "$CURRENT" != "$IMAGE_TAG" ]; then
  echo "Retour à la version en service : $CURRENT" >&2
  IMAGE_TAG="$CURRENT" docker compose up -d --no-build --wait --wait-timeout "$TIMEOUT"
  sh infra/scripts/smoke-test.sh "$URL"
  remove_images "$IMAGE_TAG"
else
  echo "Aucune version précédente connue : arrêt de la pile." >&2
  docker compose down
fi
exit 1
