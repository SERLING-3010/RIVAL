# Sprint 7 — Modo manager: fichas, monedas RIVAL y mercado de fichajes — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** manejar el equipo se siente como un juego de gestión, pero con partidos y personas reales: cada jugador tiene una ficha con estadísticas reales, cada equipo un presupuesto de monedas virtuales que gana jugando, y los DT se compran y venden jugadores en un mercado donde **el jugador siempre acepta**.

**Spec:** documento del Sprint 0, secciones 4.2.2, 6.1, 7.5, 7.6 y 9.3 (RIV-015, RIV-016). Decisión del dueño: monedas virtuales, no se compran ni se venden con dinero real.

## Reglas

- **Planilla del partido:** con el resultado confirmado, el administrador de cada equipo registra quién jugó (miembros actuales) y los goles de cada uno; la suma de goles no supera el marcador del equipo. Se puede corregir; cada corrección queda en la auditoría.
- **Ficha del jugador (RIV-016):** partidos, goles, victorias, empates y derrotas, calculados solo de partidos con resultado confirmado y planilla. Nada de atributos inventados.
- **Monedas RIVAL:** enteros, en un libro de movimientos (solo sumas y restas, nunca se edita un asiento). El saldo nunca es negativo. [SUPUESTO] Presupuesto inicial 1.000 al crear el equipo; por partido confirmado +50 a cada equipo, +100 extra al ganador, +25 extra a cada uno si empatan.
- **Mercado (RIV-015):** el administrador marca como transferible a un jugador con rol PLAYER (no al DT ni al capitán). Otro administrador del mismo deporte ofrece monedas (1 a 1.000.000, sin superar su saldo). El administrador dueño acepta o rechaza; **después el jugador acepta o rechaza**. Solo con las dos aceptaciones se mueve el jugador y las monedas, en una sola transacción con los dos equipos bloqueados en orden fijo. Las demás ofertas por ese jugador se cancelan.
- Una oferta activa por equipo comprador y jugador. El comprador puede retirarla mientras no se complete.
- Auditoría: planilla, movimientos de monedas y cada paso del traspaso.
- Centro de salud: saldo negativo (S0); traspaso completado sin aceptación del jugador (S0).

## [SUPUESTO] Fuera de este Sprint

- Valoraciones de compañeros, préstamos por un partido, ventanas de traspasos por liga, alineación visual y convocatoria, recompensa por juego limpio.

## Tareas

- [x] Dominio `manager_rules.py` con pruebas.
- [x] Persistencia `models_manager.py`.
- [x] Servicios: `coin_service.py`, `lineup_service.py`, `transfer_service.py`, `manager_queries.py`; recompensas al confirmar resultado; presupuesto inicial al crear equipo; chequeos de salud.
- [x] API `routes_manager.py`, `schemas_manager.py`.
- [x] App: modo manager del equipo, mercado, ficha del jugador, planilla del partido y ofertas para el jugador.
- [x] Verificación y `docs/sprint-07.md`.
- [ ] Revisión independiente y prueba de concurrencia en PostgreSQL (pendientes).
