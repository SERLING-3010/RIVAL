# Sprint 1 — Registro por rol, equipos y Mi equipo

- **Fecha:** 23/11/2026
- **Meta (PO):** una persona se registra con su rol y sus deportes, crea un equipo o pide entrar a uno, y ve Mi equipo.
- **Estado:** Implementado y verificado en el entorno de desarrollo; pendiente de prueba en emulador o teléfono.

## Historias cubiertas

| ID | Historia | Estado |
| --- | --- | --- |
| RIV-001 | Registro por rol (jugador, DT, árbitro, establecimiento) con deportes; menores rechazados | Verificado |
| RIV-002 | Agregar otro rol a la cuenta (`POST /me/roles`) | Verificado (API; sin pantalla aún) |
| RIV-003 | Buscar equipo o crearlo; solicitar unirse; el administrador aprueba | Verificado |
| RIV-004 | Mi equipo: plantilla, administrador, solicitudes | Verificado |
| RIV-005 | Sin DT, el capitán administra; traspaso auditado | Verificado |
| RIV-006 | Agentes libres | Pasa al Sprint 2 |

## Loop 4 — Verificación (salidas reales del 23/11/2026)

| Verificación | Comando | Resultado |
| --- | --- | --- |
| Pruebas backend | `python -m pytest -q` | 80 aprobadas, 0 fallidas |
| Tipos de la app | `npx tsc --noEmit` | 0 errores |
| Pruebas de reglas locales | `npm test` | 4 aprobadas |
| Empaquetado Android | `npx expo export --platform android` | Compila (bundle de 1,6 MB) |
| Servidor real | `uvicorn app.main:app` + registro con `curl` | Responde 201 con token; `/docs` cerrado fuera de depuración |
| Vulnerabilidades Python | `pip-audit -r requirements.txt` | Ninguna conocida |
| Vulnerabilidades npm | `npm audit --omit=dev` | 3 moderadas en herramientas de compilación de Expo (minimatch); la corrección automática bajaría Expo a la versión 52, así que no se aplicó |
| Líneas por archivo | conteo en `backend/` y `mobile/src` | Ninguno pasa de 150 |
| `any` y `TODO` | búsqueda en el código | Ninguno |
| App en emulador o teléfono | — | NO EJECUTADO (requiere tu equipo) |
| Accesibilidad con lector de pantalla | — | NO EJECUTADO |

## Revisión independiente

Un revisor que no escribió el código revisó el backend y la app. Confirmó que no hay IDOR, que no se filtran correos ni fechas de nacimiento, que no hay inyección SQL y que la regla de edad es correcta. Encontró estos problemas, ya corregidos con pruebas:

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| ALTO | La cadena de auditoría podía bifurcarse con escrituras simultáneas (en PostgreSQL) | Fila `audit_head` bloqueada con `FOR UPDATE`, `prev_hash` único, posición en la cadena y versión incluidas en el hash | `test_fork_with_same_prev_hash_is_rejected`, `test_deleting_last_event_is_detected` |
| MEDIO | Dos DT o dos capitanes posibles con peticiones simultáneas | Índices únicos parciales en la base y bloqueo de la fila del equipo | `test_database_rejects_second_captain` |
| MEDIO | El cambio de administrador no se auditaba al aprobar un DT o nombrar capitán | Evento `TEAM_ADMIN_CHANGED` siempre que cambia; aviso en la app antes de ceder la administración | `test_approving_coach_records_admin_change`, `test_captain_admin_naming_new_captain_hands_over_admin` |
| MEDIO | Registro e inicio de sesión sin límite por IP; memoria del limitador sin tope | Ventana deslizante por IP (10 registros/hora, 30 inicios/15 min) y purga | `test_register_is_limited_per_ip`, `test_login_limiter_memory_is_bounded` |
| MEDIO | App: una sesión vencida no cerraba la sesión | Manejador global de 401 | Revisión de código (sin pruebas de componentes aún) |
| MEDIO | App: el arranque podía quedarse cargando si falla el almacenamiento seguro | Lectura del token dentro del `try` | Revisión de código |
| MEDIO | App: el doble toque podía crear dos equipos | Cerrojo síncrono `useSubmitLock` | Revisión de código |
| MEDIO | App: la búsqueda no pedía la página 2 | Botón "Cargar más" | Revisión de código |
| BAJO | Árbitros o establecimientos podían unirse a un equipo | Requiere rol de jugador o DT | `test_referee_cannot_request_to_join` |
| BAJO | `%` y `_` actuaban como comodines en la búsqueda | `autoescape=True` | `test_search_treats_percent_literally` |
| BAJO | Registro simultáneo con el mismo correo daba 500 | Se captura y responde 409 | Revisión de código |
| BAJO | El tiempo límite no cubría la lectura de la respuesta | Se lee el cuerpo antes de soltar el temporizador | Revisión de código |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | El registro responde "correo ya existe", lo que permite saber si una cuenta existe (mitigado con el límite por IP) | Verificación por correo en el Sprint de endurecimiento |
| MEDIO | La app no tiene pruebas automáticas de componentes ni de hooks | Agregar `jest-expo` en el Sprint 2 |
| MEDIO | Los bloqueos de concurrencia solo se probaron en SQLite | Probar con PostgreSQL en el Sprint 2 |
| BAJO | Detrás de un proxy, la IP del límite debe venir de un encabezado de confianza [POR VERIFICAR] | Configurable al desplegar |
| BAJO | Las sesiones vencidas no se purgan | Tarea programada en el Sprint de endurecimiento |
| BAJO | Inicios de sesión fallidos no se auditan | Centro de salud (Sprint 4) |
| BAJO | La URL del backend es `http` en desarrollo | Exigir `https` en producción |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -v
cd mobile; npm run typecheck; npm test
```
