# Sprint 3 — Contrato del partido con firmas

- **Fecha:** 23/11/2026
- **Meta (PO):** cuando un DT acepta una oferta nace el contrato del partido; los dos administradores pactan las condiciones y el partido queda firmado solo cuando ambos firman la misma versión. Cada cambio después de firmar exige la aceptación del rival.
- **Estado:** Implementado y verificado en SQLite; pendiente de PostgreSQL, de la prueba en emulador o teléfono y de la revisión independiente humana.

## Historias cubiertas

| ID | Historia | Estado |
| --- | --- | --- |
| RIV-009 | Pactar condiciones y que ambos firmen; contrato firmado inmutable; cambios = versión nueva aceptada por el rival | Verificado (SQLite) |
| Deuda S1/S2 | Pruebas de componentes de la app con jest-expo | Hecho: 8 pruebas (contrato, propuesta y ofertas) |

## Decisiones

- El contrato nace solo al aceptar una oferta (índice único por búsqueda y por oferta). La versión 1 copia de la oferta la hora, el árbitro y el lugar, y pone valores por defecto: 60 min, uniformes "Oscuro"/"Claro", cambios ilimitados, cancha y árbitro mitad y mitad, aviso de 24 h [SUPUESTO: editables por cualquiera de los dos].
- Las versiones nunca se editan; solo se insertan. Las firmas van en tabla aparte, una por equipo y versión (restricción única).
- Proponer un cambio equivale a firmarlo por el equipo que propone. El rival firma esa versión o contrapropone.
- Firmar exige el número de versión: si cambió mientras el otro la leía, responde 409 `CONTRACT_VERSION_CHANGED`.
- Tras firmar, un cambio pone el contrato "En negociación" pero la versión firmada sigue vigente y visible. Si el rival rechaza (o quien propuso retira), vuelve "Firmado" con la versión anterior.
- Cancelar exige motivo (5–200 caracteres) y solo antes de la hora de inicio vigente. Después de esa hora tampoco se aceptan cambios.
- Sin dinero en la app: el reparto de cancha y árbitro es solo un acuerdo escrito (mitad, local o visitante), sin montos.
- Sin árbitro se puede pactar quién cobra las faltas dudosas; con árbitro ese campo se rechaza (`FOUL_CALLER_ONLY_WITHOUT_REFEREE`).
- Un usuario que administra los dos equipos del partido no puede firmar por ambos (`SAME_ADMIN_BOTH_TEAMS`).
- "Listo para jugar", resultado y disputa quedan para RIV-012 y RIV-013.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET | `/api/v1/teams/{id}/contracts` | Miembros del equipo |
| GET | `/api/v1/contracts/{id}` | Miembros de los dos equipos; para el resto, 404 |
| POST | `/api/v1/contracts/{id}/proposals` | Administrador de un equipo del partido |
| POST | `/api/v1/contracts/{id}/sign` | Administrador que aún no firmó la versión vigente |
| POST | `/api/v1/contracts/{id}/reject-amendment` | Administrador; solo con un cambio pendiente sobre un contrato firmado |
| POST | `/api/v1/contracts/{id}/cancel` | Administrador, con motivo |

`POST /offers/{id}/accept` ahora devuelve también `contract_id`.

## Loop 4 — Verificación (salidas reales del 23/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 164 aprobadas, 4 omitidas (son las de PostgreSQL); 25 nuevas del contrato |
| `pytest` en PostgreSQL 16 + PostGIS | NO EJECUTADO: no hay PostgreSQL en este equipo |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 14 aprobadas (6 nuevas del contrato) |
| Pruebas de componentes (`jest`, jest-expo 58) | 8 aprobadas |
| Auditoría encadenada | `verify_chain` válida tras crear y firmar (`test_every_step_is_audited`) |
| `npm audit --omit=dev` | Las mismas 3 moderadas de los Sprints 1 y 2 en herramientas de Expo; las herramientas de pruebas agregan 19 moderadas solo de desarrollo |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` en lo nuevo |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia (la revisión independiente queda pendiente)

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| MEDIO | Se podía proponer un cambio (incluso una hora nueva) después de que el partido firmado ya había empezado | `MATCH_ALREADY_STARTED` para proponer y cancelar, según la hora de la versión firmada | `test_no_changes_or_cancel_after_kickoff_of_signed_version` |
| BAJO | El script del Sprint 2 fallaba al contar líneas de archivos vacíos con `Set-StrictMode` | `@(Get-Content ...).Count` en `rival-sprint-02.ps1` | Ejecución real del script |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | Dos firmas o una firma y un cambio simultáneos solo están protegidos por FOR UPDATE + restricción única, sin prueba en PostgreSQL | Agregar caso a `test_concurrency_pg.py` y correrlo con PostgreSQL |
| MEDIO | Sin migraciones versionadas: hay 3 tablas nuevas y la base de desarrollo se recrea | Alembic antes del piloto |
| MEDIO | Catálogo real de barrios de Barranquilla pendiente [POR VERIFICAR] | Igual que en el Sprint 2 |
| BAJO | La app no avisa al rival cuando hay algo por firmar (solo la marca en "Partidos pactados") | Notificaciones push en un Sprint posterior |
| BAJO | Advertencia de Starlette por usar `httpx` en el cliente de pruebas | Revisar al actualizar dependencias |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd mobile; npm run typecheck; npm test
```
