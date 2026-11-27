# Sprint 22 — El equipo en modo juego

- **Fecha:** 25/11/2026
- **Meta (PO):** llevar a la app la pantalla del equipo aprobada en el lienzo (página «Modo manager»), con tres pestañas: Titulares sobre la cancha, Jugadores en cartas y Comparar con un hexágono.
- **Estado:** Verificado en SQLite, en PostgreSQL 16 local y en las pruebas de la app. El dueño lo probó en el iPhone, y los ajustes que pidió quedaron aplicados en este sprint y en el 23.

## Decisiones

- **Plantilla** (`squad_queries.squad`, `GET /teams/{id}/squad`): cada miembro trae media, carta, posición, rol (DT o C), partidos, goles, victorias, valoración, tripletes e insignias, todo calculado con la misma fórmula de la carta del Sprint 20. Solo la ven los miembros del equipo (`require_member`), porque incluye la alineación, que el rival no debe ver.
- **Titulares:** muestra la alineación táctica guardada para el próximo partido (Sprint 19). Si no hay ninguna, muestra una sugerida por media en la primera formación de la modalidad, marcada como «sugerida».
- **Media del equipo:** promedio de las medias de los titulares que se muestran.
- **Encabezado:** récord G-E-P, nivel Glicko-2 e insignias del equipo.
- **Comparar:** seis datos reales de dos jugadores (partidos, goles, victorias, valoración, check-ins e insignias), en un hexágono con `react-native-svg` (dependencia aprobada) y barras enfrentadas. La carta del jugador suma `check_ins`.
- **Cartas en la plantilla:** son la misma carta grande de la ficha, a escala (`ScaledCard` y `CardFront`).
  - Tocar la carta la voltea ahí mismo; mantenerla presionada (450 ms) abre la ficha del jugador.
  - **Volteo nítido:** el volteo usa `Animated.timing` y no resorte. Con resorte, iOS dejaba el texto borroso unos milisegundos (lo reportó el dueño).
- **Acceso:** botón «Plantilla (modo juego)» en el equipo.

## Pedidos del dueño durante el sprint (25/11/2026)

1. Las cartas de Jugadores, iguales a las de Titulares.
2. Las cartas de Titulares y Jugadores, iguales a la de la ficha.
3. Tocar para voltear y mantener presionado para abrir la ficha.
4. Quitar el borroso al voltear.

Los cuatro quedaron hechos.

## Loop 4 — Verificación (salidas reales del 25/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite y en PostgreSQL 16 local | Todas aprobadas; se corrieron junto con el Sprint 23 (ver `docs/sprint-23.md`) |
| `tsc --noEmit` | 0 errores |
| Pruebas de la app (`node --test` y `jest`) | Todas aprobadas (ver `docs/sprint-23.md`) |
| Líneas por archivo / `any` | Ninguno pasa de 150; sin `any` |
| En el iPhone | Probado por el dueño; ajustes aplicados |

## Riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| BAJO | Muchas cartas animadas en la plantilla | Medir el rendimiento en un teléfono real antes del piloto |
