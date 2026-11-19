#!/usr/bin/env bash
# Crea (o recrea) la base de datos EntreCOL+ en MariaDB.
# Uso:  sudo ./scripts/instalar_bd.sh            -> crea si no existe
#       sudo ./scripts/instalar_bd.sh --recrear  -> BORRA la base y la crea de nuevo
set -euo pipefail
cd "$(dirname "$0")/.."

[[ -f .env ]] || { echo "Falta .env (copia .env.example a .env y ajustalo)"; exit 1; }
APP_PASS=$(grep -E '^DB_PASSWORD=' .env | cut -d= -f2-)
[[ -n "$APP_PASS" ]] || { echo "DB_PASSWORD vacio en .env"; exit 1; }

MYSQL=${MYSQL:-mariadb}

if [[ "${1:-}" == "--recrear" ]]; then
  echo "Borrando base entrecol..."
  $MYSQL -e "DROP DATABASE IF EXISTS entrecol;"
fi

$MYSQL < db/01_esquema.sql
$MYSQL < db/02_seguridad.sql
$MYSQL < db/03_triggers.sql
sed "s/__APP_PASSWORD__/${APP_PASS//\//\\/}/g" db/04_usuario_app.sql | $MYSQL

echo "Base entrecol lista. Tablas:"
$MYSQL -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='entrecol';"
echo "Siguiente paso:  uv run python scripts/crear_admin.py"
