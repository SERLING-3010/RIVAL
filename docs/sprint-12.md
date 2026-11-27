# Sprint 12 — Moderación y confianza

- **Fecha:** 24/11/2026
- **Meta (PO):** que la comunidad pueda reportar agresiones, inasistencias y perfiles falsos; que un equipo pueda bloquear a otro; y que las sanciones las aplique una persona, con motivo y con apelación (Sprint 0, sección 4.8).
- **Estado:** Verificado en SQLite y en PostgreSQL 16 local (moderación, bloqueos, concurrencia y migración `0003`). Pendiente: emulador o teléfono, revisión independiente (y legal de los textos) y el `npm test` en rojo del CI.

## Historias cubiertas (Sprint 0, 4.8 y P1 "reputación y reportes")

| Tema | Estado |
| --- | --- |
| Reportes por agresión, inasistencia o perfil falso | Verificado |
| Bloqueo | Verificado, entre equipos |
| Sanciones aplicadas por una persona, con motivo | Verificado (advertencia o suspensión de 1 a 30 días) |
| Apelación | Verificado, decidida por otro moderador (cuatro ojos) |
| Reputación pública del equipo | No incluida (ver riesgos) |

## Decisiones

- **Moderadores fuera de los roles de registro:** tabla propia; se nombran solo con `python -m app.tools.grant_moderator correo` (auditado). Nadie puede elegir ser moderador al registrarse ni desde la app.
- **Reportes:** a una persona o a un equipo (no a uno mismo ni al propio equipo), con categoría y descripción de 10 a 500 caracteres; máximo 5 por persona en 24 horas. Un reporte nunca sanciona por sí solo.
- **Decisión:** el moderador descarta o sanciona, siempre con motivo. No ve ni decide reportes en los que está involucrado. [SUPUESTO] Si el reporte es contra un equipo, se sanciona a su administrador actual.
- **Suspensión:** la persona puede entrar, ver la app y apelar, pero cualquier acción (todo lo que no sea lectura) responde 403 `ACCOUNT_SUSPENDED` con la fecha de fin. Se aplica en un solo lugar: la dependencia del usuario actual.
- **Apelación:** una por sanción, dentro de 14 días; la decide un moderador distinto del que sancionó. Revocar levanta la suspensión. El centro de salud marca como S0 una apelación decidida por el mismo moderador.
- **Bloqueo entre equipos:** el administrador bloquea a otro equipo; mientras dure, ninguno ve al otro en rivales ni en búsquedas de partido, ni puede retarlo u ofertarle (las acciones responden como si el otro no existiera). Se puede desbloquear.
- Migración `0003` (4 tablas). La plantilla corregida en el Sprint 10 ya generó el import correcto sin tocar nada.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| POST | `/api/v1/reports` | Cualquier usuario |
| GET | `/api/v1/moderation/me` | El usuario: si es moderador y sus sanciones |
| GET · POST | `/api/v1/moderation/reports` · `/{id}/dismiss` · `/{id}/sanction` | Moderadores |
| POST | `/api/v1/sanctions/{id}/appeal` | La persona sancionada (permitido aunque esté suspendida) |
| GET · POST | `/api/v1/moderation/appeals` · `/{id}/decide` | Otro moderador |
| GET · POST | `/api/v1/teams/{id}/blocks` · `/blocks/{otro}/remove` | Administrador del equipo |

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 276 aprobadas, 10 omitidas (las de PostgreSQL); 9 nuevas |
| Moderación, bloqueos y concurrencia en PostgreSQL 16.2 local | 19 aprobadas |
| Migraciones `0001` → `0003` en PostgreSQL y `alembic check` | Sin diferencias |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 37 aprobadas (3 nuevas) |
| Pruebas de componentes (`jest`) | 31 aprobadas (3 nuevas) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| ALTO | Agregar "moderador" a los roles habría permitido registrarse como moderador | Tabla propia y nombramiento solo por línea de comandos |
| MEDIO | Una suspensión que impide entrar impediría también apelar | Suspensión de solo lectura: se puede entrar, ver y apelar |
| BAJO | `MatchFlow.tsx` pasaba de 150 líneas | Búsqueda de rivales en `RivalsFlow.tsx` |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| ALTO | `npm test` falla en el CI de GitHub | Leer el registro con sesión iniciada |
| MEDIO | Textos de reportes y sanciones sin revisión legal (Ley 1581, debido proceso) [POR VERIFICAR] | Revisión con abogado antes del piloto |
| MEDIO | Sin reputación pública del equipo (por ejemplo, inasistencias confirmadas) | Decidir con el dueño qué se publica |
| BAJO | No hay bloqueo entre personas (solo entre equipos) | Si el piloto lo pide |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m app.tools.grant_moderator correo@ejemplo.com
cd backend; .\venv\Scripts\python.exe -m alembic upgrade head
cd mobile; npm run typecheck; npm test
```
