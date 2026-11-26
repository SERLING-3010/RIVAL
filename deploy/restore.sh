#!/usr/bin/env sh
# Restaurar una copia de la base de RIVAL (Sprint 28). REEMPLAZA los datos actuales.
# Uso:  ./restore.sh backups/rival_2026-12-01_0315.dump
# Pruébalo antes del piloto en un servidor de prueba: una copia que nunca se restauró no es una copia.
set -eu

cd "$(dirname "$0")"
FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -s "$FILE" ]; then
  echo "Indica un archivo de copia que exista, por ejemplo: ./restore.sh backups/rival_2026-12-01_0315.dump" >&2
  exit 1
fi

printf 'Esto reemplaza TODOS los datos actuales con %s. Escribe RESTAURAR para seguir: ' "$FILE"
read -r ANSWER
[ "$ANSWER" = "RESTAURAR" ] || { echo "Cancelado."; exit 1; }

# Se detienen la API y los procesos para que nadie escriba durante la restauración.
docker compose stop api avisos mantenimiento
docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner' < "$FILE"
docker compose up -d api avisos mantenimiento
echo "Restauración terminada. Revisa https://<tu-dominio>/api/v1/health"
