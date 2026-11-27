# Sprint 24 — Notificaciones push

- **Fecha:** 25/11/2026
- **Meta (PO):** que nadie se pierda un reto, una convocatoria o un gol especial por confirmar (vence a las 72 horas) por no haber abierto la app.
- **Estado:** Verificado en SQLite, en PostgreSQL 16 local y en las pruebas de la app. Falta recibir un aviso real en el iPhone.

## Decisiones del dueño (25/11/2026)

1. **Avisos breves y sin datos.** El texto pasa por Expo y por Apple o Google, y se ve en la pantalla bloqueada. Por eso nunca lleva nombres, equipos, marcadores, horarios ni lugares; el detalle se ve dentro de la app. Ejemplos: «Hay un gol por confirmar», «Tienes una convocatoria nueva».
2. **Librería y proyecto de Expo:** se instaló `expo-notifications` y se creó el proyecto `@sergiolra3010/rival` en la cuenta Expo del dueño con `eas init`. Su `projectId` quedó en `app.json`.

## Decisiones técnicas

- **Los avisos salen de «Pendientes»** (Sprint 11): no hubo que tocar cada flujo. En cada ronda, para cada persona con un teléfono registrado, se avisa una sola vez por cada pendiente nuevo (tabla `push_sent`, clave «tipo:id»). Si hay varios a la vez, va un solo aviso: «Tienes N cosas nuevas por revisar en RIVAL».
- **Al registrar el teléfono**, lo que ya estaba pendiente se marca como visto, para no llegar con una ráfaga de avisos viejos.
- **Teléfonos** (tabla `push_device`, migración `0012`):
  - Se guarda solo el identificador de Expo; se valida su formato (`INVALID_PUSH_TOKEN`).
  - Hasta 5 teléfonos por persona (`TOO_MANY_DEVICES`).
  - Si el teléfono cambia de cuenta, el identificador pasa a la cuenta nueva.
  - Al cerrar sesión se quita.
  - Si Expo responde `DeviceNotRegistered`, se borra.
- **Enviador** (`python -m app.tools.push_worker`, cada minuto, o `--once` para una tarea programada): primero marca los avisos y confirma en la base, y después llama a Expo, para no dejar una llamada externa dentro de la transacción. Usa la biblioteca estándar (`urllib`), sin dependencias nuevas en el backend. En las pruebas nunca se llama a Expo.
- **App:**
  - Al iniciar sesión pide el permiso. iOS lo pregunta una sola vez; si se niega, la app sigue igual.
  - Obtiene el identificador con el `projectId` y lo registra en el backend.
  - Con la app abierta, el aviso se muestra arriba. Al tocar un aviso se abre «Pendientes».
  - **Si algo falla** (sin permiso, sin red o Expo Go sin soporte), no se registra y no se muestra ningún error.
- **Rutas:** `POST /me/push-devices` y `POST /me/push-devices/remove` (204).
- **No se avisa todavía:** las ofertas nuevas a una búsqueda de partido y las cartas nuevas, porque no son «Pendientes». Quedan para otro sprint.

## Loop 4 — Verificación (salidas reales del 25/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 364 aprobadas, 10 omitidas (las de PostgreSQL) |
| `pytest` completo en PostgreSQL 16 local | 374 aprobadas, 0 omitidas |
| Migración `0012` en PostgreSQL vacío | `upgrade`, `alembic check` sin diferencias, `downgrade` y otra vez `upgrade` |
| `tsc --noEmit` | 0 errores |
| Pruebas de la app (`node --test` / `jest`) | 62 / 81 aprobadas |
| Enviador contra la base del teléfono (`--once`) | Corre sin errores (aún sin teléfonos registrados) |
| En el iPhone | POR VERIFICAR: aceptar el permiso y recibir un aviso real |

## Riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | Expo Go en iOS con SDK 58 podría no entregar avisos remotos [POR VERIFICAR] | Probarlo; si no llegan, hace falta una «development build» con EAS |
| MEDIO | El enviador recorre los pendientes de cada persona con teléfono cada minuto | Bien para el piloto; si crece, pasar a eventos o a un intervalo mayor |
| BAJO | Un pendiente que se resuelve y vuelve con el mismo id no se avisa de nuevo | Aceptado por ahora |
