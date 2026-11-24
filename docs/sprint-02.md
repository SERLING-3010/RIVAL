# Sprint 2 — Rivales, retos, ofertas y agentes libres

- **Fecha:** 23/11/2026
- **Meta (PO):** un DT encuentra rival por cercanía, barrio o ciudad, lo reta o publica una búsqueda abierta que recibe ofertas al estilo InDriver; los jugadores sin equipo aparecen como agentes libres y aceptan invitaciones.
- **Estado:** Implementado y verificado en SQLite y PostgreSQL 16; pendiente de prueba en emulador o teléfono y del catálogo real de barrios.

## Historias cubiertas

| ID | Historia | Estado |
| --- | --- | --- |
| RIV-006 | Agentes libres por deporte; el DT invita y el jugador acepta | Verificado |
| RIV-007 | Buscar rivales por cercanía, barrio o ciudad, con rango de distancia | Verificado (cercanía con catálogo sintético) |
| RIV-008 | Retar o publicar búsqueda abierta; ofertas, contraofertas, aceptar, rechazar, retirar, cancelar | Verificado |

## Decisiones

- ADR-006: la cercanía se calcula entre centros de barrio del catálogo; nunca hay coordenadas de personas ni de equipos.
- Árbitro opcional en la búsqueda (con, sin, cualquiera); la oferta debe decidir con o sin.
- Lugar: establecimiento, informal (parque, cancha de barrio) o por acordar.
- Aceptar una oferta deja la búsqueda en "Rival encontrado"; el contrato con firmas llega en el Sprint 3.

## Loop 4 — Verificación (salidas reales del 23/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 139 aprobadas, 4 omitidas (son las de PostgreSQL) |
| `pytest` en PostgreSQL 16 + PostGIS | 143 aprobadas, incluidas 4 de concurrencia repetidas 3 veces |
| Prueba de humo con servidor real y PostgreSQL | Registro → equipos → rivales → búsqueda → oferta → aceptar → MATCHED |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`npm test`) | 8 aprobadas (edad, fechas en hora de Colombia, rangos) |
| Empaquetado Android | Compila |
| `pip-audit` | Sin vulnerabilidades (se actualizó pytest a 9.0.3 por PYSEC-2026-1845) |
| `npm audit --omit=dev` | Las mismas 3 moderadas del Sprint 1 en herramientas de Expo |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión independiente

Sin hallazgos ALTO. Confirmó: no se filtran coordenadas, los retos directos solo los ve el retado, invitaciones y solicitudes no se mezclan. Corregido con pruebas:

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| MEDIO | Se podía ofertar por id a una búsqueda fuera de tu alcance o ciudad | Regla de visibilidad compartida entre feed y oferta | `test_offer_outside_publisher_scope_is_not_found` |
| MEDIO | Aceptar y retirar a la vez dejaba datos inconsistentes | Retirar bloquea la búsqueda igual que aceptar | `test_accept_and_withdraw_at_once_stay_consistent` (PostgreSQL) |
| MEDIO | Se podía ofertar o aceptar una hora pasada | `OFFER_IN_PAST` en dominio y al aceptar; la app propone una hora futura | `test_offer_in_the_past_rejected` |
| MEDIO | El contador del administrador sumaba invitaciones | Solo cuenta solicitudes | `test_admin_counter_ignores_invitations` |
| MEDIO | Un agente libre seguía visible tras unirse por solicitud | Aprobar la solicitud lo desactiva | `test_joining_by_request_removes_free_agent` |
| MEDIO | La app solo mostraba 20 rivales o agentes | "Cargar más" con páginas acumuladas | Revisión de código |
| MEDIO | Doble toque al aceptar una invitación podía dar error 500 | Se relee tras el bloqueo (también en solicitudes) | `test_double_tap_accept_invitation_joins_once` (PostgreSQL) |
| MEDIO | El feed recortaba antes de filtrar y hacía muchas consultas | Filtro por barrio en SQL y conteo agrupado | Pruebas de feed existentes |
| BAJO | La versión de la oferta volvía a 1 tras retirarla | Máximo + 1 por equipo y búsqueda | `test_version_keeps_growing_after_withdraw` |
| BAJO | La app no dejaba ver ni retirar la oferta propia | Botón "Ver mi oferta"; acciones ocultas si la búsqueda cerró | Revisión de código |
| BAJO | Se podía retar a un equipo de otra ciudad | `INVALID_CHALLENGE` | `test_challenge_other_city_rejected` |
| BAJO | Invitaciones sin tope | Máximo 20 pendientes y 7 días de espera tras un rechazo | `test_reinvite_after_rejection_waits_a_week` |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | Catálogo real de barrios de Barranquilla pendiente [POR VERIFICAR] | Descargar el "Mapa de Barrios según el POT" de datos.gov.co y convertirlo a centroides |
| MEDIO | Sin migraciones versionadas: la base de desarrollo se recrea | Alembic antes del piloto |
| MEDIO | La app sigue sin pruebas de componentes | jest-expo en el Sprint 3 |
| BAJO | Límites de búsqueda en memoria por proceso | Redis al desplegar con varios procesos |
| BAJO | `/free-agents` lo puede consultar cualquier usuario (dato opcional del jugador, con límite) | Revisar con el abogado los textos de autorización |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
$env:RIVAL_TEST_DATABASE_URL = "postgresql+psycopg://rival:clave@127.0.0.1/rival_test"; .\venv\Scripts\python.exe -m pytest -q
cd mobile; npm run typecheck; npm test
```
