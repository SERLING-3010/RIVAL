# Sprint 8 — Calendario y tabla de la liga, árbitros en los partidos

- **Fecha:** 24/11/2026
- **Meta (PO):** que una liga funcione de punta a punta: el organizador arma el calendario, cada partido nace como contrato, la tabla sale sola de los resultados confirmados y el coordinador arbitral asigna árbitros cuyo resultado vale por sí solo.
- **Estado:** Implementado y verificado en SQLite; pendiente de PostgreSQL, de la prueba en emulador o teléfono y de la revisión independiente humana.

## Historias y pendientes cubiertos

| Tema | Estado |
| --- | --- |
| P1 del Sprint 0: calendario y tabla de liga | Verificado (SQLite) |
| P1 del Sprint 0: coordinador arbitral que asigna árbitros a los partidos | Verificado (SQLite) |
| RIV-013, parte que faltaba: resultado válido "o con la del árbitro" | Verificado: el árbitro aceptado fija el resultado y resuelve disputas |
| Riesgo del Sprint 4: "las disputas no tienen quién las resuelva" | Resuelto en partidos de liga con árbitro; los amistosos siguen sin árbitro |

## Decisiones

- **Calendario:** todos contra todos por el método del círculo; con número impar, un equipo descansa cada fecha y el local se alterna. Lo genera una sola vez el organizador o un coorganizador, con al menos 2 equipos aprobados.
- [SUPUESTO] Cada fecha comparte día y hora (la primera la elige el organizador; las siguientes cada 1–14 días) y la última debe caer dentro de 60 días, la misma regla de los contratos. Los equipos cambian hora y lugar negociando el contrato.
- Cada partido del calendario es un contrato **sin búsqueda ni oferta** (`request_id` y `offer_id` ahora son opcionales; nuevo `league_id`), con árbitro WITH y lugar "por acordar". Reutiliza firmas, cambios, reservas de cancha, resultado, planilla, monedas y actividad.
- **Tabla:** 3 puntos por victoria, 1 por empate, solo resultados confirmados. Orden: puntos, diferencia de goles, goles a favor y nombre (sin tildes).
- **Árbitros:** asignan el organizador, coorganizadores o el coordinador arbitral, solo a partidos de su liga y solo árbitros aprobados del cuerpo arbitral. Una asignación activa por partido (índice único parcial). El árbitro acepta o rechaza.
- **Resultado del árbitro:** con asignación aceptada, partido firmado y la hora ya pasada, el árbitro fija el marcador: queda CONFIRMED (`by_referee`) aunque los equipos no coincidan. Si ya estaba confirmado, no se cambia. Paga las monedas del partido igual que un resultado confirmado por los equipos.
- El árbitro ve sus partidos en "Mis partidos como árbitro" con lo mínimo (equipos, liga, hora, lugar, resultado). No ve el contrato completo.
- Todo queda en la auditoría: calendario, asignación, respuesta y resultado del árbitro.
- [SUPUESTO] Fuera de este Sprint: calendario de ida y vuelta, fechas por partido, reprogramar o borrar el calendario, cancelar una asignación desde la app, calificar al árbitro, pantalla para nombrar personal.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| POST | `/api/v1/leagues/{id}/fixtures` | Organizador o coorganizador |
| GET | `/api/v1/leagues/{id}/calendar` · `/api/v1/leagues/{id}/table` | Cualquier usuario |
| POST | `/api/v1/contracts/{id}/referee` | Personal de la liga |
| GET | `/api/v1/me/referee-matches` | El árbitro |
| POST | `/api/v1/referee-assignments/{id}/accept` · `/decline` | El árbitro asignado |
| POST | `/api/v1/contracts/{id}/referee-result` | El árbitro asignado que aceptó |

`GET /contracts/{id}` incluye `league_id`, `referee` y `result.by_referee`; `request_id` puede ser `null`.

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 244 aprobadas, 4 omitidas (son las de PostgreSQL); 13 nuevas |
| `pytest` en PostgreSQL 16 + PostGIS | NO EJECUTADO: no hay PostgreSQL ni Docker en este equipo |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 30 aprobadas (2 nuevas) |
| Pruebas de componentes (`jest`) | 23 aprobadas (3 nuevas: calendario, asignar árbitro, partidos del árbitro) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia (la revisión independiente queda pendiente)

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| MEDIO | Crear un contrato estaba atado a una oferta | `create_contract` genérico; la oferta y la liga lo usan | Toda la suite de contratos |
| MEDIO | La actividad del partido fallaría con contratos de liga (sin búsqueda ni oferta) | Filtros opcionales | `test_api_league_matches` (lee la actividad indirectamente) y revisión de código |
| BAJO | La tabla ordenaba "Águilas" después de "Bravos" por la tilde | Orden por nombre normalizado | `test_standings_points_and_tiebreaks` |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| ALTO | Acciones simultáneas (firmas, reservas, traspasos, resultado del árbitro y de los equipos a la vez) sin prueba en PostgreSQL | Sprint de endurecimiento: instalar PostgreSQL o Docker y ampliar `test_concurrency_pg.py` |
| MEDIO | Sin migraciones: columnas nuevas en `match_contract` y `match_result`, 2 tablas nuevas | Alembic antes del piloto |
| MEDIO | Un error del organizador en el calendario no se puede deshacer | Reprogramar o borrar el calendario mientras no haya partidos firmados |
| BAJO | El personal de la liga no ve el contrato completo de partidos donde no juega | Vista de partido para el personal |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd mobile; npm run typecheck; npm test
```
