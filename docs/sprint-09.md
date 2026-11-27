# Sprint 9 — Endurecimiento: PostgreSQL real, migraciones y CI

- **Fecha:** 24/11/2026
- **Meta (PO):** cerrar el riesgo técnico más alto de los Sprints 3 a 8 —acciones simultáneas probadas solo en SQLite— y dejar la base lista para un piloto: migraciones versionadas, CI que lo verifique en cada push y los pendientes de seguridad del Sprint 1.
- **Estado:** Verificado en PostgreSQL 16 local (no solo en SQLite). El CI queda escrito y validado localmente, pero solo corre cuando la rama llegue a GitHub.

## Pendientes que cierra

| De | Tema | Estado |
| --- | --- | --- |
| Sprints 3–8 (ALTO) | Firmas, reservas, traspasos y resultado del árbitro simultáneos sin prueba en PostgreSQL | Cerrado: 6 pruebas nuevas, 10 de 10 aprobadas tres veces seguidas en PostgreSQL 16.2 |
| Sprints 2–8 (MEDIO) | Sin migraciones versionadas | Cerrado: Alembic con revisión inicial `0001` |
| Sprint 1 (BAJO) | Inicios de sesión fallidos no se auditaban (el error deshacía la transacción) | Cerrado: se auditan en una transacción aparte, sin correo |
| Sprint 1 (BAJO) | Las sesiones vencidas no se purgan | Cerrado: `app.tools.purge_sessions` |

## Decisiones

- **Pruebas de concurrencia nuevas** (dos acciones a la vez en sesiones distintas): dos firmas a la vez, firmar mientras el rival propone un cambio, dos confirmaciones de reserva sobre la misma franja, último reporte y corrección a la vez (monedas pagadas una sola vez), dos jugadores aceptando traspasos que juntos superan el saldo del comprador, y árbitro y equipo confirmando a la vez.
- **PostgreSQL sin instalar nada global:** `pgserver` (PyPI) trae los binarios de PostgreSQL 16 y corre dentro del entorno del backend; es opcional (`requirements-pg-local.txt`, `dev_tools/local_pg.py`). No hace falta PostGIS: el código no usa funciones geográficas (la cercanía se calcula en Python con los centros de barrio).
- **Migraciones:** Alembic 1.20.1. La URL sale de `RIVAL_DATABASE_URL`, nunca de `alembic.ini`. La revisión `0001` se generó contra PostgreSQL y se revisó a mano: índices únicos parciales y la fila génesis de `audit_head`. `render_as_batch` para que también funcione en SQLite. Desarrollo y pruebas siguen usando `create_schema`.
- [SUPUESTO] Las migraciones generadas son la excepción a la regla de 150 líneas (la `0001` tiene unas 780): son código generado, no se editan salvo para revisarlas.
- **Inicio de sesión fallido:** se audita como `LOGIN_FAILED` con una clave seudónima (SHA-256 del correo normalizado), el id de la cuenta si existe y el motivo. Nunca el correo ni la IP. El centro de salud avisa (S1) si una clave acumula 20 fallos en una hora.
- **CI (GitHub Actions):** backend en SQLite y en PostgreSQL 16 (con migraciones: subir, `alembic check` y bajar), app (`npm ci`, `tsc`, pruebas) y reglas del proyecto (150 líneas, sin `any`). Sin secretos ni despliegue; las credenciales son de un PostgreSQL desechable del propio CI.

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 248 aprobadas, 10 omitidas (las de PostgreSQL) |
| `pytest` en PostgreSQL 16.2 (pgserver) | 257 aprobadas, 0 omitidas, en 5 min 36 s |
| Pruebas de concurrencia, 3 corridas seguidas | 10/10, 10/10, 10/10 |
| `alembic upgrade head` → `check` → `downgrade base` → `upgrade head` en PostgreSQL | Sin diferencias con los modelos |
| `alembic upgrade head` + `check` en SQLite y centro de salud sobre esa base | Sin diferencias; "Hallazgos: 0" |
| `tests/test_migrations.py` | Aprobada |
| Workflow de CI | YAML válido (leído con js-yaml); reglas de 150 líneas y `any` probadas localmente. NO EJECUTADO en GitHub todavía |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150 (salvo la migración generada); sin `any` ni `TODO` |

## Revisión propia

| Impacto | Hallazgo | Acción |
| --- | --- | --- |
| — | Ninguna prueba de concurrencia nueva encontró un fallo: los bloqueos y los índices de los Sprints 3–8 se comportan en PostgreSQL como se diseñaron | Quedan como regresión en el CI |
| BAJO | Durante el sprint se descargó por error la rueda de `pgserver` antes de pedir permiso; se borró sin instalarla, se pidió permiso y luego se instaló con aprobación | Registrado aquí por transparencia |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | El CI no se ha ejecutado en GitHub; puede necesitar ajustes la primera vez | Revisar el primer run tras el push |
| MEDIO | El registro sigue diciendo "correo ya existe" (permite saber si una cuenta existe) | Verificación por correo: requiere un servicio de envío [POR VERIFICAR] |
| BAJO | `purge_sessions` no está programado en ningún servidor | Tarea programada al desplegar |
| BAJO | Advertencia de Starlette por `httpx` en el cliente de pruebas | Revisar al actualizar dependencias |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; $env:RIVAL_TEST_DATABASE_URL = (.\venv\Scripts\python.exe dev_tools\local_pg.py); .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m alembic upgrade head
cd mobile; npm run typecheck; npm test
```
