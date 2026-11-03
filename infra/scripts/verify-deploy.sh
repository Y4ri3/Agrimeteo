#!/bin/sh
# Rejoue déploiement, échec et retour arrière sur une pile jetable (C-06, C-07), sans toucher à la pile en service.
set -eu
cd "$(dirname "$0")/../.."
[ -f .env ] || cp .env.example .env

export COMPOSE_PROJECT_NAME=agrimeteo-verify
export FRONTEND_PORT="${VERIFY_PORT:-18080}"
export IMAGE_KEEP=0
DEPLOY_STATE_DIR="$(mktemp -d)"
export DEPLOY_STATE_DIR

cleanup() {
  IMAGE_TAG=verify-1 docker compose down -v >/dev/null 2>&1 || true
  for N in 1 2 3 4; do
    docker image rm "agrimeteo-backend:verify-$N" "agrimeteo-frontend:verify-$N" >/dev/null 2>&1 || true
  done
  rm -rf "$DEPLOY_STATE_DIR"
}
trap cleanup EXIT

expect_running() {
  RUNNING="$(docker inspect -f '{{.Config.Image}}' "$(docker compose ps -q backend)")"
  [ "$RUNNING" = "agrimeteo-backend:$1" ] || { echo "ÉCHEC : $RUNNING en service, $1 attendue" >&2; exit 1; }
  echo "OK : $1 en service"
}

echo "--- 1. Première version"
IMAGE_TAG=verify-1 sh infra/scripts/deploy-local.sh
expect_running verify-1

echo "--- 2. Mise à jour"
IMAGE_TAG=verify-2 sh infra/scripts/deploy-local.sh
expect_running verify-2

echo "--- 3. Version en échec : le smoke test ne passe pas, retour automatique"
if IMAGE_TAG=verify-3 SMOKE_BASE_URL=http://localhost:1 sh infra/scripts/deploy-local.sh; then
  echo "ÉCHEC : le déploiement aurait dû échouer" >&2
  exit 1
fi
expect_running verify-2
[ "$(cat "$DEPLOY_STATE_DIR/current.tag")" = verify-2 ] || { echo "ÉCHEC : current.tag modifié" >&2; exit 1; }

echo "--- 4. Retour arrière manuel"
sh infra/scripts/rollback.sh
expect_running verify-1

echo "--- 5. Nouvelle version : les anciennes images sont supprimées"
IMAGE_TAG=verify-4 sh infra/scripts/deploy-local.sh
expect_running verify-4
if docker image inspect agrimeteo-backend:verify-2 >/dev/null 2>&1; then
  echo "ÉCHEC : verify-2 aurait dû être supprimée" >&2
  exit 1
fi
docker image inspect agrimeteo-backend:verify-1 >/dev/null
echo "OK : verify-2 supprimée, verify-1 gardée pour le retour arrière"

echo "Vérification du déploiement réussie"
