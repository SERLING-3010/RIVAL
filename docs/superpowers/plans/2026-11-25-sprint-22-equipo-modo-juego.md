# Sprint 22 — Equipo en modo juego (plan)

**Meta:** llevar a la app la pantalla del equipo aprobada en el lienzo (página "Modo manager"): Titulares sobre la cancha, Jugadores en cartas y Comparar con hexágono.

## Reglas

- **Plantilla:** cada miembro con media, nivel, posición, rol (DT, C) y partidos, calculados con la misma fórmula de la carta (Sprint 20).
- **Titulares:** la alineación táctica guardada para el próximo partido (Sprint 19). Si no hay ninguna, una sugerida por media en la primera formación de la modalidad, marcada como sugerida.
- **Media del equipo:** promedio de las medias de los titulares mostrados.
- **Encabezado:** récord G-E-P, nivel Glicko-2 e insignias ganadas del equipo.
- **Comparar:** seis datos reales de dos jugadores: partidos, goles, victorias, valoración, check-ins e insignias.
- Solo la ven los miembros del equipo (incluye la alineación, que el rival no debe ver).
- Dependencia nueva: `react-native-svg` (aprobada) para el hexágono.

## Tareas

- [x] `services/squad_queries.py` y ruta `GET /teams/{id}/squad`; la carta suma `check_ins`.
- [x] Pruebas de servicio y de API.
- [x] App: modelos y reglas de la cancha, pantalla con tres pestañas, hexágono con SVG, acceso desde el equipo.
- [x] Pruebas, tsc, prettier, 150 líneas; prueba en el iPhone.
- [x] Verificar en PostgreSQL; `docs/sprint-22.md`.
