#!/bin/sh
# À lancer UNE FOIS sur le serveur, avec sudo, depuis une copie du dépôt :
#   git clone https://github.com/Y4ri3/Agrimeteo.git && cd Agrimeteo
#   DEPLOY_USER=<utilisateur> sudo -E sh infra/scripts/setup-vps.sh
# Prépare le dossier de déploiement, le fichier .env et le site nginx. Peut être relancé sans risque.
set -eu
DOMAIN="${DOMAIN:-devops.yokkutelabs.com}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/agrimeteo}"
DEPLOY_USER="${DEPLOY_USER:-${SUDO_USER:-}}"
HERE="$(cd "$(dirname "$0")/../.." && pwd)"

[ "$(id -u)" -eq 0 ] || { echo "Lancez ce script avec sudo." >&2; exit 1; }
[ -n "$DEPLOY_USER" ] || { echo "Indiquez l'utilisateur de déploiement : DEPLOY_USER=<nom> sudo -E sh $0" >&2; exit 1; }
id "$DEPLOY_USER" >/dev/null 2>&1 || { echo "Utilisateur inconnu : $DEPLOY_USER" >&2; exit 1; }

MISSING=""
for cmd in docker nginx rsync; do command -v "$cmd" >/dev/null 2>&1 || MISSING="$MISSING $cmd"; done
docker compose version >/dev/null 2>&1 || MISSING="$MISSING docker-compose-v2"
[ -z "$MISSING" ] || { echo "À installer d'abord :$MISSING" >&2; exit 1; }
id -nG "$DEPLOY_USER" | tr ' ' '\n' | grep -qx docker \
  || echo "ATTENTION : $DEPLOY_USER n'est pas dans le groupe docker (sudo usermod -aG docker $DEPLOY_USER, puis reconnexion)."

# 1. Dossier de déploiement : le code y est copié par la CI ; .env et infra/deploy (versions) y restent.
mkdir -p "$DEPLOY_PATH"
chown "$DEPLOY_USER" "$DEPLOY_PATH"
if [ -f "$DEPLOY_PATH/.env" ]; then
  echo ".env déjà présent, non modifié : $DEPLOY_PATH/.env"
else
  sed -e 's/^APP_ENV=.*/APP_ENV=demo/' -e 's/^WEATHER_PROVIDER=.*/WEATHER_PROVIDER=open_meteo/' \
    "$HERE/.env.example" >"$DEPLOY_PATH/.env"
  chown "$DEPLOY_USER" "$DEPLOY_PATH/.env"
  chmod 600 "$DEPLOY_PATH/.env"
  echo ".env créé (données météo réelles : WEATHER_PROVIDER=open_meteo)"
fi

# 2. Site nginx. Un fichier déjà présent n'est jamais écrasé : certbot y a peut-être ajouté le HTTPS.
if [ -d /etc/nginx/sites-available ]; then
  SITE=/etc/nginx/sites-available/"$DOMAIN".conf
else
  SITE=/etc/nginx/conf.d/"$DOMAIN".conf
fi
if [ -f "$SITE" ]; then
  echo "Site nginx déjà présent, non modifié : $SITE"
else
  sed "s/devops\.yokkutelabs\.com/$DOMAIN/g" "$HERE/infra/nginx/devops.yokkutelabs.com.conf" >"$SITE"
  echo "Site nginx installé : $SITE"
fi
[ -d /etc/nginx/sites-enabled ] && [ "$SITE" != "/etc/nginx/conf.d/$DOMAIN.conf" ] && ln -sf "$SITE" /etc/nginx/sites-enabled/"$DOMAIN".conf
nginx -t
if command -v systemctl >/dev/null 2>&1; then systemctl reload nginx; else nginx -s reload; fi

cat <<MSG

Serveur prêt. Il reste à faire :
  1. DNS : un enregistrement A (et AAAA si IPv6) de $DOMAIN vers l'adresse de ce serveur.
  2. HTTPS : sudo certbot --nginx -d $DOMAIN
  3. GitHub : ajouter les secrets VPS_HOST, VPS_USER, VPS_SSH_KEY et VPS_KNOWN_HOSTS (docs/exploitation.md).
Le premier déploiement se fait ensuite tout seul à la fusion dans main.
MSG
