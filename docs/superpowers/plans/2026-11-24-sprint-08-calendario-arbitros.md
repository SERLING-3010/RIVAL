# Sprint 8 — Calendario y tabla de la liga, árbitros en los partidos — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** el organizador genera el calendario de la liga (todos contra todos) y cada partido nace como contrato; la tabla de posiciones sale sola de los resultados confirmados; el coordinador arbitral asigna un árbitro del cuerpo arbitral a cada partido, el árbitro acepta, y su resultado vale por sí solo (también resuelve disputas).

**Spec:** documento del Sprint 0, secciones 4.2.1, 4.4.1, 4.5, 4.7 y 9.2 (P1: calendario y tabla de liga, coordinador arbitral) y RIV-013 ("válido con ambas confirmaciones **o la del árbitro**").

## Reglas

- **Calendario:** lo genera una sola vez el organizador o un coorganizador, con al menos 2 equipos aprobados. Algoritmo de todos contra todos (método del círculo; con número impar, un equipo descansa por fecha). Cada fecha tiene día y hora: la primera la elige el organizador y las siguientes van cada N días (1 a 14). [SUPUESTO] La última fecha debe caer dentro de 60 días, la misma regla de los contratos.
- Cada partido del calendario crea un contrato **sin búsqueda ni oferta**, ligado a la liga, con árbitro WITH y lugar "por acordar". Los dos administradores lo negocian y firman como cualquier contrato (pueden cambiar hora y lugar).
- **Tabla:** solo resultados confirmados de partidos de la liga. 3 puntos por victoria, 1 por empate. Orden: puntos, diferencia de goles, goles a favor, nombre.
- **Árbitro:** lo asigna el organizador, un coorganizador o el coordinador arbitral, solo a partidos de su liga y solo a árbitros aprobados del cuerpo arbitral. Una asignación activa por partido. El árbitro acepta o rechaza; quien asignó puede cancelar y asignar otro.
- **Resultado del árbitro:** el árbitro con asignación aceptada reporta el marcador cuando ya pasó la hora firmada; el resultado queda CONFIRMED con ese marcador aunque los equipos no coincidan (resuelve la disputa). Si los equipos ya lo habían confirmado, no se cambia.
- El árbitro ve sus partidos asignados con lo mínimo: equipos, hora, lugar y resultado. Nunca correos.
- Auditoría de calendario, asignaciones y resultado del árbitro.

## Tareas

- [x] Dominio `fixture_rules.py` (todos contra todos, fechas) y `standings_rules.py` (tabla) con pruebas.
- [x] Persistencia: contrato con `league_id` y búsqueda/oferta opcionales; `league_fixture`; `referee_assignment`.
- [x] Servicios `fixture_service.py`, `standings_queries.py`, `referee_service.py`.
- [x] API: calendario, tabla, asignación, respuesta del árbitro, resultado del árbitro, mis partidos como árbitro.
- [x] App: calendario y tabla en la liga, asignar árbitro en el contrato, "Mis partidos como árbitro".
- [x] Verificación y `docs/sprint-08.md`.
- [ ] Revisión independiente y prueba de concurrencia en PostgreSQL (pendientes).
