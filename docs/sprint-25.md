# Sprint 25 — Retos y ofertas en «Pendientes», con aviso

- **Fecha:** 25/11/2026
- **Meta (PO):** que el aviso más importante llegue: «Tienes un reto nuevo». También, que el dueño de una búsqueda se entere cuando le llegan ofertas.
- **Estado:** Verificado en SQLite, en PostgreSQL 16 local y en las pruebas de la app. Falta recibir un aviso real en el iPhone.

## Decisiones

- **Te retaron** (`CHALLENGE_RECEIVED`): es una búsqueda abierta y vigente dirigida a tu equipo, en la que tu equipo todavía no tiene una oferta pendiente.
  - Le aparece al administrador del equipo retado, con el título «Te retaron: {equipo}».
  - Lleva al muro de búsquedas de su equipo (destino `feed`), donde responde con una oferta.
  - Al ofertar, el pendiente desaparece.
- **Ofertas para tu búsqueda** (`OFFERS_RECEIVED`): son ofertas pendientes en una búsqueda abierta de tu equipo.
  - Se muestra un pendiente por búsqueda, con la cantidad («Ofertas para tu búsqueda (2)»).
  - Lleva a la pantalla de ofertas de esa búsqueda (destino `offers`), donde el dueño acepta o rechaza.
- **Ambos son urgentes** si la búsqueda empieza en menos de 24 horas.
- **Avisos** (Sprint 24), siempre breves y sin datos:
  - Los textos son «Tienes un reto nuevo.» y «Hay ofertas nuevas para tu búsqueda.».
  - La clave del aviso ahora incluye una huella corta del título del pendiente (SHA-1 sin uso criptográfico). Así, dos retos al mismo equipo o una oferta más en la misma búsqueda generan un aviso nuevo, y un pendiente que no cambia no se repite.
- **Sin migración:** las fuentes nuevas están en `pending_match_sources.py`, y se calculan en cada consulta como el resto de «Pendientes».

## Loop 4 — Verificación (salidas reales del 25/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 366 aprobadas, 10 omitidas (las de PostgreSQL) |
| `pytest` completo en PostgreSQL 16 local | 376 aprobadas, 0 omitidas |
| `tsc --noEmit` | 0 errores |
| Pruebas de la app (`node --test` / `jest`) | 62 / 81 aprobadas |
| En el iPhone | El teléfono del dueño ya está registrado para avisos (1 en la base); falta recibir un aviso real |

## Riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| BAJO | Las cartas especiales nuevas todavía no generan aviso, porque se otorgan al abrir la ficha | Otorgarlas al confirmar resultado o gol, y entonces avisar |
