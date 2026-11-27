# Sprint 28 — Despliegue listo (Docker)

- **Fecha:** 25/11/2026
- **Meta (PO):** que poner RIVAL en un servidor sea levantar un `docker compose`, sin depender todavía de qué proveedor se elija.
- **Estado:** Verificado en local (flujo del contenedor contra PostgreSQL). La imagen y el `docker compose` los verifica el CI de GitHub en el primer push.

## Decisiones

- **Una sola imagen** (`backend/Dockerfile`, Python 3.12 slim):
  - Corre con un usuario sin privilegios.
  - Las dependencias van en una capa aparte, para que se reutilice si no cambian.
  - Sirve para la API, las migraciones, el enviador de avisos y la limpieza de sesiones; solo cambia el comando.
- **`deploy/docker-compose.yml`:**
  - Servicios: `db` (PostgreSQL 16 con volumen), `migrate` (sube las migraciones y termina), `api`, `avisos` y `mantenimiento`.
  - La API solo escucha en `127.0.0.1`; la publica un proxy HTTPS.
- **Las tablas las crea Alembic, no el arranque:** la variable nueva `RIVAL_AUTO_SCHEMA` vale `true` en desarrollo y `false` en el contenedor. Antes, el arranque siempre creaba las tablas, y eso chocaba con `alembic upgrade`.
- **Salud:** `GET /api/v1/health` responde 200 si la base contesta y 503 si no. No pide autenticación ni muestra datos.
- **IP real detrás del proxy:** uvicorn corre con `--proxy-headers` y `FORWARDED_ALLOW_IPS`. Sin esto, todos compartirían el límite de intentos de la IP del proxy.
- **Dependencias de producción** (`requirements-prod.txt`): las de ejecución más el driver de PostgreSQL. En desarrollo el driver ya venía en `requirements-dev.txt`.
- **Copias de seguridad:**
  - `deploy/backup.sh` hace un `pg_dump -Fc` diario con 14 días de retención.
  - `deploy/restore.sh` pide confirmación escribiendo RESTAURAR y detiene la API durante la restauración.
  - Hay que copiar los archivos fuera del servidor.
- **Secretos:** solo en `deploy/.env`, que está en `.gitignore`. `deploy/.env.example` tiene valores de ejemplo y ningún secreto real.
- **CI** (trabajo nuevo «Despliegue (Docker)»): construye la imagen, levanta todo, comprueba la salud y que las migraciones estén al día, hace una copia y la restaura.

## Loop 4 — Verificación (salidas reales del 25/11/2026)

| Verificación | Resultado |
| --- | --- |
| Flujo del contenedor contra PostgreSQL 16 local (base vacía, `alembic upgrade head`, API con `RIVAL_AUTO_SCHEMA=false`) | Salud `{"status":"ok"}`, registro 201, `/docs` oculto (404), `alembic check` sin diferencias |
| `pytest` en SQLite | 373 aprobadas, 10 omitidas (las de PostgreSQL, que corren en el CI) |
| Sintaxis de `backup.sh` y `restore.sh` (`sh -n`) y de los YAML | Válida |
| Construir la imagen y levantar con Docker | Sin Docker en este equipo: lo verifica el CI de GitHub (trabajo «Despliegue (Docker)») [POR VERIFICAR hasta que corra] |

## Pendiente

- (D) Elegir el proveedor del servidor y el dominio. Luego, los pasos de `docs/despliegue.md`.
- (D+C) Compilar la app para el piloto, apuntando al dominio con HTTPS (EAS/TestFlight).
