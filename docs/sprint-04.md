# Sprint 4 — Resultado, central de actividad y centro de salud

- **Fecha:** 23/11/2026
- **Meta (PO):** después de jugar, los dos administradores reportan el marcador y el resultado vale cuando coinciden; cada equipo y cada partido muestran quién hizo cada cambio; un chequeo detecta los estados que nunca deberían existir.
- **Estado:** Implementado y verificado en SQLite; pendiente de PostgreSQL, de la prueba en emulador o teléfono y de la revisión independiente humana.

## Historias cubiertas

| ID | Historia | Estado |
| --- | --- | --- |
| RIV-013 | Confirmar el resultado: vale con los dos reportes iguales; si no, disputa | Verificado sin árbitro (SQLite) |
| RIV-014 | Central de actividad por equipo y por partido, con antes y después | Verificado (SQLite) |
| Sprint 1 → 4 | Centro de salud con invariantes deterministas | Verificado: herramienta de línea de comandos |

## Decisiones

- [SUPUESTO] La confirmación por árbitro llega con RIV-010 (árbitros); hoy solo cuentan los dos administradores.
- [SUPUESTO] Solo marcador: sin W.O. ni tarjetas en este Sprint.
- Se reporta solo un partido firmado, no cancelado y cuya hora de la versión firmada ya pasó. Un cambio pendiente sin aceptar no impide reportar: vale lo firmado.
- Un reporte por equipo, corregible hasta que el resultado quede confirmado. Confirmado = inmutable. Cada reporte y corrección queda en la auditoría (RESULT_REPORTED, RESULT_DISPUTED, RESULT_CONFIRMED).
- La app oculta "Proponer cambios", "Firmar" y "Cancelar" cuando el partido ya empezó (el backend ya lo impedía) y muestra el formulario de marcador.
- La actividad del equipo incluye equipo, solicitudes e invitaciones, búsquedas, ofertas y contratos. Nunca eventos de cuenta (registro, sesiones) ni correos. Máximo 100 eventos, del más reciente al más antiguo.
- El evento de oferta aceptada ahora se registra antes del de contrato creado, para que la actividad se lea en orden.
- Centro de salud: cadena de auditoría rota (S0), contrato firmado sin dos firmas (S0), equipo activo sin administrador (S1), búsqueda con rival sin contrato (S1), partido sin resultado confirmado 48 h después (S3). `python -m app.tools.health_check` termina con código 1 si hay S0 o S1. Solo lee.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| POST | `/api/v1/contracts/{id}/result` | Administrador de un equipo del partido |
| GET | `/api/v1/contracts/{id}/activity` | Miembros de los dos equipos; para el resto, 404 |
| GET | `/api/v1/teams/{id}/activity` | Miembros del equipo; para el resto, 403 |

`GET /contracts/{id}` incluye `result`; `GET /teams/{id}/contracts` incluye `result_status` y marcador.

## Loop 4 — Verificación (salidas reales del 23/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 182 aprobadas, 4 omitidas (son las de PostgreSQL); 18 nuevas |
| `pytest` en PostgreSQL 16 + PostGIS | NO EJECUTADO: no hay PostgreSQL en este equipo |
| `python -m app.tools.health_check` sobre base nueva | "Hallazgos: 0", código 0 |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 16 aprobadas (2 nuevas) |
| Pruebas de componentes (`jest`) | 12 aprobadas (4 nuevas: marcador y actividad) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia (la revisión independiente queda pendiente)

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| MEDIO | Las pruebas de la app del Sprint 3 dependían de la fecha real y habrían fallado desde el 25/11/2026 | Reglas reciben `now`; los datos de prueba usan fechas relativas | `tests/contract.test.ts`, `__tests__/fixtures.ts` |
| BAJO | La app mostraba "Proponer cambios" y "Cancelar" después de la hora del partido | `contractActions` usa la hora vigente | `después de la hora: no se cambia ni se cancela` |
| BAJO | En la actividad, "contrato creado" aparecía antes que "oferta aceptada" | Orden de eventos al aceptar | `test_contract_activity_shows_who_did_what` |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | Reportes simultáneos y firmas simultáneas sin prueba en PostgreSQL | Agregar a `test_concurrency_pg.py` y correrlo |
| MEDIO | Las disputas no tienen quién las resuelva (sin árbitro ni moderación) | Árbitro (RIV-010) y moderación (sección 4.8) |
| MEDIO | Sin migraciones: 2 tablas nuevas (`match_result`, `match_result_report`) | Alembic antes del piloto |
| BAJO | Inicios de sesión fallidos siguen sin auditarse: el error deshace la transacción | Escribirlos en una transacción aparte en el Sprint de endurecimiento |
| BAJO | El centro de salud no tiene pantalla: no existe rol de administrador del sistema | Panel web de administración (`web_admin/`) |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m app.tools.health_check
cd mobile; npm run typecheck; npm test
```
