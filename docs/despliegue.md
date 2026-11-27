# Desplegar RIVAL (Sprint 28)

Guía para poner el backend en un servidor con Docker. Sirve para cualquier proveedor (un VPS en DigitalOcean, Hetzner, AWS Lightsail, etc.). Cuando elijas uno, solo cambian el paso 1 y el dominio.

## Qué se levanta

Todo está en `deploy/docker-compose.yml` y usa una sola imagen del backend (`backend/Dockerfile`):

| Servicio | Qué hace |
| --- | --- |
| `db` | PostgreSQL 16, con los datos en un volumen (`pgdata`) |
| `migrate` | Sube las migraciones (`alembic upgrade head`) y termina; los demás esperan a que salga bien |
| `api` | La API en `127.0.0.1:8000`, sin crear tablas al arrancar (`RIVAL_AUTO_SCHEMA=false`) |
| `avisos` | El enviador de notificaciones push, cada minuto |
| `mantenimiento` | Borra las sesiones vencidas una vez al día |

La API no se publica directo a internet. La publica un proxy HTTPS (paso 4).

## Pasos

1. **Servidor:** Linux con Docker y el plugin `docker compose`. Basta con 1 vCPU y 2 GB de RAM para el piloto.
2. **Código y secretos:**
   ```sh
   git clone https://github.com/SERLING-3010/RIVAL.git && cd RIVAL/deploy
   cp .env.example .env   # y cambia POSTGRES_PASSWORD por una clave larga y única
   ```
   El `.env` nunca va al repositorio: está en `.gitignore`.
3. **Arrancar:**
   ```sh
   docker compose up -d --build
   docker compose ps                  # migrate debe salir con código 0; los demás en running
   curl http://127.0.0.1:8000/api/v1/health   # {"status":"ok"}
   ```
4. **HTTPS:** pon un proxy delante de `127.0.0.1:8000` con un dominio propio. Lo más simple es Caddy, que saca y renueva el certificado solo:
   ```
   api.tu-dominio.com {
       reverse_proxy 127.0.0.1:8000
   }
   ```
   Con el proxy en el mismo servidor, `FORWARDED_ALLOW_IPS=127.0.0.1` está bien. Así los límites de intentos se cuentan por la IP real de cada persona y no por la del proxy.
5. **La app:** compila la app apuntando al servidor, con `EXPO_PUBLIC_API_URL=https://api.tu-dominio.com`.
6. **Datos iniciales:**
   ```sh
   docker compose run --rm api python -m app.tools.import_neighborhoods <archivo.csv>
   docker compose run --rm api python -m app.tools.grant_moderator <correo>
   ```

## Copias de seguridad

- **Diaria, desde cron:** `15 3 * * * cd /ruta/a/RIVAL/deploy && ./backup.sh >> backups/backup.log 2>&1`. Deja un archivo por día en `deploy/backups/` y borra los de más de 14 días.
- **Fuera del servidor:** copia esos archivos a otro lugar (otro disco o almacenamiento en la nube). Una copia guardada solo en el servidor se pierde con él.
- **Restaurar:** `./restore.sh backups/rival_AAAA-MM-DD_HHMM.dump`. Pide escribir RESTAURAR, detiene la API mientras tanto y reemplaza todos los datos.
- **Prueba antes del piloto:** restaura una copia en un servidor de prueba. El CI ya hace una copia y la restaura en cada cambio (trabajo «Despliegue (Docker)»).

## Actualizar a una versión nueva

```sh
cd RIVAL && git pull && cd deploy
./backup.sh                      # siempre, antes de actualizar
docker compose up -d --build     # migrate sube las migraciones nuevas antes de que arranque la API
```

## Revisar que todo esté bien

- **Salud:** `curl https://api.tu-dominio.com/api/v1/health` responde `ok` (200) o `db_unavailable` (503).
- **Registros:** `docker compose logs -f api avisos`.
- **Revisión de datos:** `docker compose run --rm api python -m app.tools.health_check` revisa la cadena de auditoría, los equipos y los contratos.
