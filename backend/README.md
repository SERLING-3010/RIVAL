# RIVAL — Backend

API FastAPI con capas:

- `app/domain`: reglas puras (edad ≥ 18, administrador del equipo, catálogo de deportes, validaciones). Sin base de datos ni HTTP.
- `app/persistence`: modelos SQLAlchemy 2. SQLite en desarrollo (ADR-003); PostgreSQL + PostGIS desde el Sprint 2.
- `app/services`: casos de uso, sesiones, límite de intentos y auditoría encadenada.
- `app/api`: rutas `/api/v1`, esquemas Pydantic (campos desconocidos se rechazan) y manejo de errores.

## Variables de entorno

| Variable | Por defecto | Uso |
| --- | --- | --- |
| `RIVAL_DATABASE_URL` | `sqlite:///./rival_dev.db` | Base de datos |
| `RIVAL_CORS_ORIGINS` | `http://localhost:8081` | Orígenes permitidos (nunca `*`) |
| `RIVAL_SESSION_TTL_HOURS` | `168` | Vida máxima de una sesión |
| `RIVAL_SESSION_IDLE_HOURS` | `72` | Cierre por inactividad |
| `RIVAL_DEBUG` | `false` | Si es `true`, publica `/docs` (solo desarrollo) |
| `RIVAL_TEST_DATABASE_URL` | SQLite en memoria | Si se define (p. ej. `postgresql+psycopg://rival:clave@127.0.0.1/rival_test`), las pruebas corren contra PostgreSQL, incluidas las de concurrencia |

## Comandos

```powershell
.\venv\Scripts\python.exe -m pytest -v
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
.\venv\Scripts\python.exe -m pip_audit -r requirements.txt   # opcional: escaneo de vulnerabilidades
.\venv\Scripts\python.exe -m app.tools.health_check          # centro de salud (código 1 si hay S0 o S1)
```

## Catálogo de barrios (ADR-006)

La búsqueda "Cerca de mí" necesita el centro de cada barrio. Se importa desde un CSV separado por `;` con encabezado `nombre;ciudad;lat;lon;fuente`:

```powershell
.\venv\Scripts\python.exe -m app.tools.import_neighborhoods C:\ruta\barrios_barranquilla.csv
```

Fuente prevista para Barranquilla: "Mapa de Barrios de Barranquilla Según el POT" en datos.gov.co [POR VERIFICAR: convertir los polígonos a centroides]. Sin catálogo, la búsqueda por barrio y por ciudad funciona igual.

## Base de datos y migraciones (Sprint 9)

- **Desarrollo y pruebas:** la API crea las tablas sola al arrancar (`create_schema`). Si tu `rival_dev.db` es de un Sprint anterior, bórrala para que se cree de nuevo.
- **Cualquier base con datos que importen (piloto, producción):** usa las migraciones de Alembic. Toman la URL de `RIVAL_DATABASE_URL`.

```powershell
$env:RIVAL_DATABASE_URL = "postgresql+psycopg://usuario:clave@servidor/rival"
.\venv\Scripts\python.exe -m alembic upgrade head
```

- **Si cambias un modelo**, genera la migración y revísala a mano antes de confirmarla. `tests/test_migrations.py` falla en el CI si un modelo cambia sin migración.

```powershell
.\venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe el cambio"
```

## Pruebas con PostgreSQL local (sin instalar PostgreSQL ni Docker)

Las pruebas de concurrencia solo corren contra PostgreSQL. El CI de GitHub Actions las corre en cada push; para correrlas en tu equipo:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-pg-local.txt
$env:RIVAL_TEST_DATABASE_URL = (.\venv\Scripts\python.exe dev_tools\local_pg.py)
.\venv\Scripts\python.exe -m pytest -q
```

## Mantenimiento

```powershell
.\venv\Scripts\python.exe -m app.tools.purge_sessions   # borra sesiones vencidas (tarea diaria)
.\venv\Scripts\python.exe -m app.tools.health_check     # centro de salud: incluye picos de inicios de sesión fallidos
```

## Endpoints del Sprint 2

`GET /api/v1/teams/{id}/rivals?scope=NEARBY|NEIGHBORHOOD|CITY&radius_km=` · `GET|POST /api/v1/me/free-agent` · `GET /api/v1/free-agents?sport=&city=&neighborhood=` · `POST /api/v1/teams/{id}/invitations` · `GET /api/v1/me/invitations` · `POST /api/v1/invitations/{id}/accept|reject` · `POST|GET /api/v1/teams/{id}/match-requests` · `GET /api/v1/teams/{id}/match-feed` · `POST /api/v1/match-requests/{id}/cancel` · `POST /api/v1/teams/{id}/match-requests/{rid}/offers` · `GET /api/v1/match-requests/{id}/offers` · `POST /api/v1/offers/{id}/accept|reject|withdraw`

## Endpoints del Sprint 1

`GET /api/v1/catalog/sports` · `POST /api/v1/auth/register` · `POST /api/v1/auth/login` · `POST /api/v1/auth/logout` · `GET /api/v1/me` · `POST /api/v1/me/roles` · `POST /api/v1/teams` · `GET /api/v1/teams` · `GET /api/v1/teams/{id}` · `GET /api/v1/me/teams` · `POST /api/v1/teams/{id}/join-requests` · `GET /api/v1/teams/{id}/join-requests` · `POST /api/v1/join-requests/{id}/approve` · `POST /api/v1/join-requests/{id}/reject` · `POST /api/v1/teams/{id}/captain` · `POST /api/v1/teams/{id}/leave`
