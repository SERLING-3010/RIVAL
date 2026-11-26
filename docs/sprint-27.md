# Sprint 27 — Preparar el piloto: términos, privacidad y mis datos

- **Fecha:** 25/11/2026
- **Meta (PO):** cumplir lo básico de la Ley 1581 de 2012 antes de abrir el piloto: autorización expresa, política de tratamiento visible y derechos de conocer y suprimir los datos. También dejar escrito qué falta para el piloto.
- **Estado:** Verificado en SQLite, en PostgreSQL 16 local y en las pruebas de la app. Falta verlo en el iPhone y que un abogado revise los textos.

## Decisiones del dueño (25/11/2026)

- **Eliminar la cuenta es anonimizarla.**
  - Se borran el correo, el nombre, la fecha de nacimiento, la ciudad, el barrio, la posición, las sesiones, los teléfonos con avisos, los perfiles de agente libre y el texto de los mensajes.
  - La persona queda como «Jugador eliminado».
  - Los partidos, los resultados y la auditoría se conservan sin esos datos. Así no se rompe la cadena de auditoría ni el historial de los equipos rivales.

## Decisiones técnicas

- **Aceptación versionada** (`legal_rules.TERMS_VERSION = "2026-11-25"`, migración `0013`):
  - Al registrarse hay que aceptar los Términos y la Privacidad, autorizar el tratamiento de datos y declarar ser mayor de 18. Sin eso responde `TERMS_NOT_ACCEPTED`.
  - Se guardan la versión y la fecha. La auditoría `USER_REGISTERED` incluye la versión.
  - Las cuentas anteriores o con una versión vieja ven «Antes de seguir» (`needs_terms`) y aceptan con `POST /me/accept-terms`. Solo se acepta la versión vigente (`TERMS_VERSION_OUTDATED`).
- **Descargar mis datos** (`GET /me/data-export`):
  - Incluye perfil, aceptación de términos, equipos, partidos, valoraciones recibidas (cantidad y promedio, sin quién las dio), mensajes escritos, horas de check-in, perfiles de agente libre y cuántos teléfonos tienen avisos.
  - No incluye datos de otras personas.
  - En la app se comparte como texto con el menú del sistema.
- **Eliminar la cuenta** (`POST /me/delete-account`):
  - Pide la contraseña (`WRONG_PASSWORD`). Responde 422 y no 401, para que la app no cierre la sesión y se pueda reintentar.
  - Exige salir antes de los equipos (`LEAVE_TEAMS_FIRST`), entregar las ligas que organiza (`LEAGUE_ORGANIZER_FIRST`) y no tener canchas (`VENUES_FIRST`), para que nadie quede sin responsable.
  - El correo pasa a `eliminado-{id}@rival.invalid`, así el original queda libre para otra cuenta.
  - La contraseña se reemplaza por una aleatoria que nadie conoce.
  - Queda en la auditoría como `ACCOUNT_DELETED`, sin datos personales.
- **App:**
  - El registro tiene una casilla con enlaces a los dos textos.
  - Las cuentas anteriores pasan por la pantalla «Antes de seguir».
  - En el inicio, «Mi cuenta» abre «Mis datos y privacidad». Ahí están los textos, descargar mis datos, eliminar la cuenta con contraseña y confirmación, y cerrar sesión.
- **Textos legales:**
  - Son borradores en `docs/legal/`, idénticos a los de la app (`legalTerms.ts`, `legalPrivacy.ts`).
  - Si cambian, hay que subir la versión en el backend y en la app.
- **Checklist del piloto:** `docs/piloto-checklist.md` dice qué falta y quién lo hace: abogado, responsable del tratamiento, servidor, copias de seguridad, distribución de la app y operación.

## Loop 4 — Verificación (salidas reales del 25/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 371 aprobadas, 10 omitidas (las de PostgreSQL) |
| `pytest` completo en PostgreSQL 16 local | 381 aprobadas, 0 omitidas |
| Migración `0013` en PostgreSQL vacío | `upgrade`, `alembic check` sin diferencias, `downgrade` y otra vez `upgrade` |
| `tsc --noEmit` | 0 errores |
| Pruebas de la app (`node --test` / `jest`) | 62 / 84 aprobadas |
| En el iPhone | POR VERIFICAR: la cuenta del dueño, anterior a los términos, debe ver «Antes de seguir» |

## Riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| ALTO | Los textos son borradores y falta el responsable del tratamiento | Revisión de un abogado antes del piloto (checklist) |
| BAJO | La edad es declarada (fecha de nacimiento), no verificada con documento | Suficiente para el piloto [POR VERIFICAR con el abogado] |
