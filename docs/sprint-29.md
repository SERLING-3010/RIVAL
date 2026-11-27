# Sprint 29 — Lanzamiento solo con fútbol

- **Fecha:** 26/11/2026
- **Meta (PO):** lanzar la app solo con fútbol, sin árbitros y sin establecimientos deportivos. Eso llega más adelante.
- **Estado:** Verificado en SQLite, en PostgreSQL 16 local y en las pruebas de la app. Falta verlo en el iPhone.

## Decisión del dueño (26/11/2026)

Lanzar solo con fútbol, sin árbitro y sin establecimiento deportivo. El resto se deja para después.

## Decisiones técnicas

- **No se borra nada; se apaga por configuración.** Hay tres variables nuevas:
  - `RIVAL_SPORTS`: los deportes disponibles, separados por coma. Vacío significa todos.
  - `RIVAL_ENABLE_REFEREES`: prende o apaga los árbitros.
  - `RIVAL_ENABLE_VENUES`: prende o apaga los establecimientos.

  Por defecto todo está prendido, para el desarrollo y las pruebas. El despliegue (`deploy/.env.example`) trae `FOOTBALL`, `false` y `false`. Para prender algo más adelante basta con cambiar el `.env` y reiniciar.
- **Backend** (`launch_rules.py`):
  - El catálogo solo trae fútbol: no se pueden crear equipos ni ligas de otros deportes.
  - Al registrarse o agregar un rol, solo se puede ser jugador o DT (`ROLE_NOT_AVAILABLE`).
  - Las rutas de árbitros y de establecimientos (canchas, franjas y reservas) responden 404 `FEATURE_DISABLED`, como si no existieran. Tampoco se puede pedir entrar al cuerpo arbitral de una liga.
  - En búsquedas, ofertas y cambios de contrato no se acepta «con árbitro» (`REFEREES_NOT_AVAILABLE`) ni «en establecimiento» (`VENUES_NOT_AVAILABLE`). «Da igual» se guarda como «sin árbitro».
  - Los partidos que crea RIVAL (calendario de liga y copa) salen sin árbitro.
  - `GET /api/v1/features` le dice a la app qué está prendido. No pide sesión.
- **App:**
  - La raíz carga una vez qué está prendido (`useLaunchFeatures`) y lo comparte con las pantallas (`FeaturesContext`).
  - Al registrarse solo aparecen Jugador y Director técnico.
  - En búsquedas, ofertas y cambios de contrato desaparece la opción de árbitro (es siempre «sin árbitro») y la de establecimiento.
  - En el contrato no aparece «Reservar cancha», y en la liga no aparece el cuerpo arbitral.
  - Si la app no logra preguntar, muestra todo, pero el backend igual rechaza lo apagado: nunca se habilita algo que no esté disponible.
- **Bot de prueba:** si los establecimientos están apagados, deja de confirmar reservas sin fallar.

## Datos del responsable fuera del código (pedido del dueño, 26/11/2026)

- **El repositorio de GitHub es público**, así que el nombre, la dirección, el correo y el teléfono del responsable del tratamiento ya no van en el texto de la política. Se configuran en el `.env` del servidor (`RIVAL_LEGAL_*`), el backend los entrega en `GET /api/v1/legal` y la app los pone en la política. Lo que falte se muestra «por definir».
- **Se quitó la cédula o NIT:** el artículo 13 del Decreto 1377 de 2013 pide nombre o razón social, domicilio, dirección, correo y teléfono, pero no un documento de identidad.
- **Para el usuario:** en «Mi cuenta» aparece «Escribir a privacidad» cuando el servidor tiene un correo configurado. Abre su app de correo con la solicitud ya armada (conocer, corregir, suprimir o revocar) y muestra los plazos de respuesta.
- **Para el dueño:** cambia sus datos de contacto sin tocar el código ni publicar una versión nueva de la app, y le llegan solicitudes ordenadas.
- La versión de los textos sube a `2026-11-26`, así que las cuentas los aceptan de nuevo.

## Loop 4 — Verificación (salidas reales del 26/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 377 aprobadas, 10 omitidas (las de PostgreSQL) |
| `pytest` completo en PostgreSQL 16 local | 387 aprobadas, 0 omitidas |
| Modo lanzamiento por API (`test_api_launch.py`) | Solo fútbol; árbitro rechazado; rutas de árbitros y canchas en 404; «con árbitro» y «establecimiento» rechazados; «da igual» pasa a «sin árbitro» |
| `tsc --noEmit` | 0 errores |
| Pruebas de la app (`node --test` / `jest`) | 64 / 85 aprobadas |
| Backend del teléfono en modo lanzamiento | `/api/v1/features` → `{"sports":["FOOTBALL"],"referees":false,"venues":false}` |
| En el iPhone | POR VERIFICAR |
