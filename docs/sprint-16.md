# Sprint 16 — Copa eliminatoria de liga

- **Fecha:** 24/11/2026
- **Meta (PO):** que una liga juegue una copa por eliminación directa (P2 del Sprint 0: "torneos eliminatorios"), reutilizando contratos, árbitros y resultados.
- **Estado:** Verificado en SQLite y en PostgreSQL 16 local (pruebas completas, concurrencia y migración `0007`). Pendiente: emulador o teléfono y revisión independiente. El `npm test` del CI queda aparte por decisión del dueño.

## Historias cubiertas

| Tema | Estado |
| --- | --- |
| El organizador arma una copa con los equipos aprobados | Verificado |
| Siembra por nivel y pases directos para los mejores | Verificado |
| El ganador avanza solo cuando se confirma el resultado (admins o árbitro) | Verificado |
| Empates definidos por penales | Verificado (los define el organizador) |
| Campeón de la copa | Verificado |
| Cuadro visible para todos en la app | Verificado en pruebas de componentes |

## Decisiones

- **Una copa por liga** (restricción única), de 2 a 32 equipos aprobados. La arma el organizador o un coorganizador.
- **Siembra:** nivel Glicko-2 de cada equipo (sin partidos, 1500); a igual nivel, el inscrito primero. Cuadro clásico (1 contra el último), así los mejores solo se cruzan al final. Si los equipos no llenan una potencia de 2, los mejores sembrados pasan directo la primera ronda.
- **Partidos:** cada cruce con sus dos equipos nace como contrato de la liga, con árbitro y lugar por acordar, igual que el calendario: los administradores lo ajustan y firman, y el coordinador arbitral puede asignar árbitro.
- **Avance:** lo dispara el resultado confirmado, tanto por los dos administradores como por el árbitro. Se bloquea la fila de la copa (`FOR UPDATE`), así dos semifinales confirmadas a la vez no crean dos finales.
- [SUPUESTO] **Empate:** el organizador registra quién ganó por penales (auditado como `CUP_TIEBREAK_SET`). Solo se puede con resultado confirmado, empatado y sin ganador.
- [SUPUESTO] **Fechas:** cada ronda tiene fecha prevista (primera fecha + días entre rondas, todas dentro de los 60 días). Si un cruce nace cuando su fecha ya pasó, se programa al día siguiente a la misma hora.
- **La copa no suma a la tabla:** la tabla de la liga ahora cuenta solo los partidos del calendario (antes contaba todo contrato de la liga, y la copa habría sumado puntos).
- Auditoría: `CUP_CREATED`, `CUP_TEAM_ADVANCED`, `CUP_TIEBREAK_SET`, `CUP_CHAMPION`.
- Migración `0007` (2 tablas).

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET | `/api/v1/leagues/{id}/cup` | Cualquier usuario |
| POST | `/api/v1/leagues/{id}/cup` (`first_kickoff`, `days_between`) | Organizador o coorganizador |
| POST | `/api/v1/cup-matches/{id}/tiebreak` (`winner_team_id`) | Organizador o coorganizador |

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 302 aprobadas, 10 omitidas (las de PostgreSQL); 10 nuevas |
| `pytest` completo en PostgreSQL 16 local | 312 aprobadas, 0 omitidas |
| Migraciones `0001` → `0007`, `alembic check`, bajar a `0006` y a `base` en PostgreSQL | Sin diferencias ni errores |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 46 aprobadas (2 nuevas) |
| Pruebas de componentes (`jest`) | 42 aprobadas (2 nuevas) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| ALTO | Los partidos de copa tienen `league_id` y la tabla contaba todo partido de la liga: la copa habría sumado puntos | La tabla cuenta solo los partidos del calendario; prueba incluida |
| MEDIO | Avanzar desde la liquidación del resultado creaba una importación circular | El avance se llama desde los dos lugares que confirman resultados, después de su registro de auditoría |
| BAJO | El formulario para armar la copa aparecía también sin conexión | Solo aparece cuando la liga no tiene copa |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | Los penales los registra el organizador, no el árbitro | Si el piloto lo pide, que el árbitro los informe con el resultado |
| BAJO | Copa de ida y vuelta, tercer puesto y reprogramar rondas no están | Según uso en el piloto |
| BAJO | Un cruce cuya fecha ya pasó se programa al día siguiente | Los administradores la ajustan como cualquier contrato |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m alembic upgrade head
cd mobile; npx tsc --noEmit; npm test
```
