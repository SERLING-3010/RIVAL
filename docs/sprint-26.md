# Sprint 26 — Cartas ganadas al momento, con aviso

- **Fecha:** 25/11/2026
- **Meta (PO):** que una carta especial se gane en el momento en que se cumple la hazaña, y que llegue «¡Ganaste una carta nueva!» aunque no se abra la app.
- **Estado:** Verificado en SQLite, en PostgreSQL 16 local y en las pruebas de la app. Falta verlo en el iPhone.

## Decisiones

- **Cartas al momento** (`card_awards`): las cartas del jugador y del equipo se vuelven a calcular cuando cambia algo que puede otorgarlas:
  - un resultado confirmado, por los dos equipos o por el árbitro: ambos equipos y quienes ya tienen planilla en ese partido;
  - la planilla guardada: sus jugadores y su equipo;
  - un gol con tipo confirmado por el rival: ese jugador;
  - una valoración recibida: el valorado;
  - el cierre de temporada: el campeón.
- **Mismo cálculo de siempre:** se reutiliza el de la ficha y la plantilla, así que la regla de cada carta vive en un solo lugar. Abrir la ficha sigue otorgando, como respaldo.
- **Avisos** (sin datos, como decidió el dueño):
  - Los textos son «¡Ganaste una carta nueva!» y «Tu equipo ganó una carta nueva.».
  - Cada carta se avisa una sola vez por persona (`CARD:{código}`, `TEAMCARD:{equipo}:{código}`).
  - Al registrar un teléfono, las cartas que ya se tenían no se avisan.
- **A dónde lleva el aviso:** el aviso trae solo el nombre de una pantalla (`open`).
  - Si es una carta tuya, abre tu ficha, donde aparece la pantalla «¡Nueva carta!» (Sprint 23).
  - Si es del equipo, abre el inicio.
  - En cualquier otro caso, abre «Pendientes».
- **Sin migración.**

## Loop 4 — Verificación (salidas reales del 25/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 368 aprobadas, 10 omitidas (las de PostgreSQL) |
| `pytest` completo en PostgreSQL 16 local | 378 aprobadas, 0 omitidas |
| `tsc --noEmit` | 0 errores |
| Pruebas de la app (`node --test` / `jest`) | 62 / 81 aprobadas |
| En el iPhone | POR VERIFICAR |

## Riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| BAJO | Confirmar un resultado ahora también recalcula las fichas y las plantillas de los dos equipos | Bien para el piloto; medirlo si el tiempo de respuesta crece |
