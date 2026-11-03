#!/bin/sh
# Extrait agrimeteo-frontend et agrimeteo-backend depuis des clones neufs, historique conservé (M-01).
# Usage : extraire-depots.sh <monorepo> <dossier_cible>. Le monorepo lui-même n'est jamais modifié.
# Prérequis : git et git-filter-repo (pip install git-filter-repo).
set -eu
SOURCE="$1"
TARGET="$2"
mkdir -p "$TARGET"
FRONTEND="$TARGET/agrimeteo-frontend"
BACKEND="$TARGET/agrimeteo-backend"

# Frontend : le contenu de frontend/ devient la racine du nouveau dépôt.
git clone --no-local "$SOURCE" "$FRONTEND"
(cd "$FRONTEND" && git filter-repo --subdirectory-filter frontend)

# Backend : backend/ et ml/ restent ensemble, chemins conservés (le Dockerfile en dépend).
git clone --no-local "$SOURCE" "$BACKEND"
(cd "$BACKEND" && git filter-repo \
  --path backend/ --path ml/ --path docs/api/ \
  --path scripts/check_openapi.py --path scripts/migration/backend.Makefile \
  --path .gitignore --path .gitattributes --path .editorconfig --path .dockerignore \
  --path-rename scripts/migration/backend.Makefile:Makefile)

echo "Dépôts extraits dans $TARGET"
