#!/bin/sh
# Contrôle les images construites : utilisateur non root (C-03), aucun secret ni fichier .env (C-04).
set -eu
TAG="${IMAGE_TAG:-local}"
FAILED=0

for SERVICE in backend frontend; do
  IMAGE="agrimeteo-$SERVICE:$TAG"

  IMAGE_USER="$(docker image inspect -f '{{.Config.User}}' "$IMAGE")"
  case "$IMAGE_USER" in
    "" | 0 | root | 0:* | root:*) echo "$IMAGE : s'exécute en root" >&2; FAILED=1 ;;
    *) echo "$IMAGE : utilisateur $IMAGE_USER" ;;
  esac

  if docker history --no-trunc "$IMAGE" | grep -iE '(password|passwd|secret|token|api[_-]?key)=' >&2; then
    echo "$IMAGE : secret possible dans l'historique" >&2
    FAILED=1
  fi

  FOUND="$(docker run --rm --entrypoint sh "$IMAGE" -c 'find / -xdev -name .env 2>/dev/null || true')"
  if [ -n "$FOUND" ]; then
    echo "$IMAGE : fichier .env présent : $FOUND" >&2
    FAILED=1
  fi
done

[ "$FAILED" -eq 0 ] && echo "images conformes"
exit "$FAILED"
