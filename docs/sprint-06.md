# Sprint 6 — Establecimientos, canchas y franjas

- **Fecha:** 24/11/2026
- **Meta (PO):** el dueño de un establecimiento registra canchas y publica franjas; el administrador de un equipo con partido firmado en cancha de establecimiento reserva la franja que cubre el partido; el establecimiento confirma. Nunca hay dos confirmaciones para la misma franja, y el contrato muestra "Listo para jugar".
- **Estado:** Implementado y verificado en SQLite; pendiente de PostgreSQL (prueba de concurrencia de confirmaciones), de la prueba en emulador o teléfono y de la revisión independiente humana.

## Historias cubiertas

| ID | Historia | Estado |
| --- | --- | --- |
| RIV-012 | Como establecimiento, registrar canchas y franjas; ninguna franja con dos confirmaciones | Verificado en SQLite (restricción en BD + prueba de servicio); concurrencia en PostgreSQL pendiente |

Con este Sprint quedan implementadas todas las historias P0 del backlog (RIV-001 a RIV-014), con los alcances y supuestos anotados en cada `docs/sprint-0N.md`.

## Decisiones

- Registra establecimientos quien tiene el rol VENUE_OWNER. La dirección es pública (es un negocio); nunca hay ubicación de personas.
- Tarifa de referencia por hora opcional, en `Decimal` exacto (`Numeric(12,2)`), viaja como texto (`"80000.00"`) y la app la formatea sin pasar por números de punto flotante. Es solo informativa: la cancha se paga en el establecimiento.
- Franjas de 30 a 240 minutos, en el futuro y hasta 60 días adelante, sin traslape en la misma cancha (intervalos semiabiertos).
- Reserva: la pide un administrador de cualquiera de los dos equipos de un contrato firmado, no cancelado, con lugar "cancha de establecimiento", antes de la hora; la franja debe cubrir inicio + duración de la versión firmada y ser del deporte del partido.
- Una reserva activa por contrato y una confirmada por franja: verificación previa, bloqueo de la franja (FOR UPDATE) e índices únicos parciales en la base de datos. Confirmar rechaza las demás pendientes de esa franja.
- Cancelar el partido cancela su reserva. Quien reservó (o el rival) puede cancelar la reserva antes de la hora.
- "Listo para jugar" = contrato firmado y, si el lugar es establecimiento, reserva confirmada. Lugar informal o por acordar no necesitan confirmación.
- Los eventos de reserva quedan en la auditoría del contrato y se ven en su actividad.
- Centro de salud: dos confirmadas en una franja (S0, no debería pasar por el índice) y reserva confirmada que ya no cubre el partido firmado (S1, por ejemplo tras un cambio de hora aceptado).
- [SUPUESTO] Fuera de este Sprint: fotos, horarios recurrentes, bloquear o borrar franjas, cancha sede de una liga, escenarios públicos con enlace oficial, verificación del establecimiento.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| POST | `/api/v1/venues` | Cuenta con rol de establecimiento |
| GET | `/api/v1/venues?city=&sport=&q=&page=` · `/api/v1/me/venues` | Cualquier usuario · el dueño |
| GET | `/api/v1/venues/{id}` | Cualquiera (reservas solo para el dueño) |
| POST | `/api/v1/venues/{id}/courts` · `/api/v1/courts/{id}/slots` | El dueño |
| POST | `/api/v1/contracts/{id}/bookings` | Administrador de un equipo del partido |
| POST | `/api/v1/bookings/{id}/confirm` · `/reject` | El dueño |
| POST | `/api/v1/bookings/{id}/cancel` | Administrador de un equipo del partido |

`GET /contracts/{id}` incluye `booking` y `ready_to_play`.

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 213 aprobadas, 4 omitidas (son las de PostgreSQL); 15 nuevas |
| `pytest` en PostgreSQL 16 + PostGIS | NO EJECUTADO: no hay PostgreSQL en este equipo |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 24 aprobadas (4 nuevas: pesos, franjas, reserva) |
| Pruebas de componentes (`jest`) | 17 aprobadas (2 nuevas de la pantalla del establecimiento) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia (la revisión independiente queda pendiente)

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| MEDIO | Cancelar el partido dejaba ocupada la franja del establecimiento | `cancel_for_contract` al cancelar | `test_cancelling_match_cancels_booking_and_requester_can_cancel` |
| BAJO | `admin_side` vivía en el servicio de contratos y obligaba a importaciones circulares | Movido a `contract_queries` | Toda la suite |
| BAJO | Una prueba esperaba mal el fin de la franja en UTC | Corregida la prueba (el código estaba bien) | `formulario de franja: hora de Colombia…` |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| ALTO | La confirmación simultánea de dos reservas sobre la misma franja no está probada en PostgreSQL (el Sprint 0 exige "restricción en BD + prueba de concurrencia") | Agregar a `test_concurrency_pg.py` y correrlo antes del piloto |
| MEDIO | Un cambio de hora aceptado después de reservar deja la reserva desfasada (el centro de salud lo detecta, pero la app no avisa) | Avisar en el contrato y pedir nueva reserva |
| MEDIO | Sin migraciones: 4 tablas nuevas | Alembic antes del piloto |
| BAJO | El dueño no puede borrar ni bloquear franjas | Sprint de establecimientos 2 |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m app.tools.health_check
cd mobile; npm run typecheck; npm test
```
