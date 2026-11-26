#!/usr/bin/env sh
# Copia de seguridad de la base de RIVAL (Sprint 28). Úsala a diario desde cron, por ejemplo:
#   15 3 * * *  cd /ruta/a/RIVAL/deploy && ./backup.sh >> backups/backup.log 2>&1
# Deja un archivo comprimido por día en deploy/backups/ y borra los de más de 14 días.
# Copia también esos archivos FUERA del servidor (otro disco o la nube): si el servidor se pierde,
# una copia guardada en él no sirve.
set -eu

cd "$(dirname "$0")"
mkdir -p backups
STAMP=$(date +%Y-%m-%d_%H%M)
FILE="backups/rival_${STAMP}.dump"

# Formato personalizado de pg_dump (-Fc): comprimido y restaurable con pg_restore.
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$FILE"

if [ ! -s "$FILE" ]; then
  echo "La copia quedó vacía: revisa que el servicio db esté corriendo." >&2
  rm -f "$FILE"
  exit 1
fi

find backups -name 'rival_*.dump' -mtime +14 -delete
echo "Copia lista: $FILE ($(wc -c < "$FILE") bytes)"
