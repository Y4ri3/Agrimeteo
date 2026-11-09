#!/bin/sh
# Construit et contrôle les images, lance la pile sur les ports de test 3100 et 8100, puis les tests e2e dans le réseau Compose.
# Le projet Compose est distinct de la pile déployée : les deux peuvent tourner sur la même machine.
set -eu
cd "$(dirname "$0")/../.."
[ -f .env ] || cp .env.example .env
mkdir -p e2e/reports

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-agrimeteo-ci}"
export FRONTEND_PORT="${CI_FRONTEND_PORT:-3100}"
C="docker compose -f docker-compose.yml -f infra/compose/docker-compose.ci.yml"
trap '$C --profile e2e down -v --remove-orphans' EXIT

$C build backend frontend
sh infra/scripts/check-images.sh
$C up -d --wait --wait-timeout "${DEPLOY_TIMEOUT:-90}" backend frontend
$C --profile e2e run --rm --build e2e
