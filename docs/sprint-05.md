# Sprint 5 — Ligas y cuerpo arbitral

- **Fecha:** 24/11/2026
- **Meta (PO):** un jugador o DT con equipo, o un árbitro, crea una liga y queda como organizador; los equipos piden inscribirse y los árbitros piden entrar al cuerpo arbitral; el personal de la liga aprueba o rechaza.
- **Estado:** Implementado y verificado en SQLite; pendiente de PostgreSQL, de la prueba en emulador o teléfono y de la revisión independiente humana.

## Historias cubiertas

| ID | Historia | Estado |
| --- | --- | --- |
| RIV-011 | Crear o buscar una liga e inscribir mi equipo; el creador es organizador y aprueba | Verificado (SQLite) |
| RIV-010 | Como árbitro, buscar ligas y unirme a su cuerpo arbitral con aprobación | Verificado (SQLite) |

## Decisiones

- Crea una liga quien tiene el rol de árbitro o es miembro de un equipo activo (Sprint 0, 4.2.1). Queda como organizador.
- Personal: organizador, coorganizador y coordinador arbitral. Solo el organizador nombra personal (API; aún sin pantalla). No se quita personal en este Sprint, así que siempre queda un organizador.
- Inscripción de equipo: la pide el administrador del equipo; mismo deporte, modalidad y ciudad que la liga (`TEAM_NOT_ELIGIBLE`). Aprueban organizador o coorganizador.
- Cuerpo arbitral: lo pide una cuenta con rol de árbitro y el deporte de la liga en su perfil. Aprueban organizador, coorganizador o coordinador arbitral.
- Una solicitud pendiente o aprobada por equipo (o árbitro) y liga: se revisa antes de insertar y un índice único parcial cubre la carrera. Quien pidió puede retirar la pendiente o salir si estaba aprobado; después puede volver a pedir.
- Cualquiera ve la liga con equipos y árbitros aprobados y el personal; solo el personal ve las solicitudes pendientes. Nunca se muestran correos.
- Los eventos de inscripción del equipo aparecen en la actividad del equipo.
- [SUPUESTO] Fuera de este Sprint: calendario, tabla, canchas sede, asignar árbitros a partidos, confirmación del resultado por árbitro, decisiones con dos organizadores y voto si el organizador abandona.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| POST | `/api/v1/leagues` | Árbitro o miembro de un equipo |
| GET | `/api/v1/leagues?sport=&city=&q=&page=` | Cualquier usuario |
| GET | `/api/v1/leagues/{id}` | Cualquier usuario (pendientes solo para el personal) |
| GET | `/api/v1/me/leagues` | El usuario: ligas donde es personal, árbitro o juega su equipo |
| POST | `/api/v1/leagues/{id}/staff` | Organizador |
| POST | `/api/v1/leagues/{id}/team-requests` | Administrador del equipo |
| POST | `/api/v1/leagues/{id}/referee-requests` | Árbitro con el deporte de la liga |
| POST | `/api/v1/league-requests/{team\|referee}/{id}/approve` · `/reject` | Personal según el tipo |
| POST | `/api/v1/league-requests/{team\|referee}/{id}/withdraw` | Quien pidió (administrador del equipo o el árbitro) |

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 198 aprobadas, 4 omitidas (son las de PostgreSQL); 16 nuevas |
| `pytest` en PostgreSQL 16 + PostGIS | NO EJECUTADO: no hay PostgreSQL en este equipo |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 20 aprobadas (4 nuevas de ligas) |
| Pruebas de componentes (`jest`) | 15 aprobadas (3 nuevas de la pantalla de liga) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia (la revisión independiente queda pendiente)

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| MEDIO | Una solicitud repetida rompía la transacción por la restricción única y dejaba la sesión inutilizable | Verificación previa con mensaje claro; el índice queda para la carrera | `test_team_enrollment_approved_by_organizer`, `test_only_organizer_adds_staff_and_once` |
| BAJO | La app compararía la ciudad del equipo y la liga con tildes y mayúsculas distintas | Comparación normalizada | `solo equipos que administro, del mismo juego y ciudad` |
| BAJO | El inicio decía "Ligas · Próximamente (Sprint 3)" | Botón real para equipos y árbitros | Revisión de código |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | Solicitudes simultáneas solo protegidas por FOR UPDATE + índice parcial, sin prueba en PostgreSQL | Agregar a `test_concurrency_pg.py` |
| MEDIO | Nombrar personal solo por API (por id de usuario); falta pantalla y buscar personas | Sprint de ligas 2 |
| MEDIO | Sin migraciones: 4 tablas nuevas | Alembic antes del piloto |
| BAJO | Cualquiera puede crear muchas ligas | Límite por usuario en el Sprint de endurecimiento |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd mobile; npm run typecheck; npm test
```
