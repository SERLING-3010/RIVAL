# Sprint 17 — Logros e insignias (plan)

**Meta:** reconocer a jugadores y equipos por lo que hacen en la cancha (P2 del Sprint 0: "logros e insignias"), sin dinero y sin que se puedan otorgar a mano.

## Reglas

- Se calculan en cada consulta a partir de datos reales: partidos con resultado confirmado, planillas (goles), check-ins y copas. No hay tabla de insignias ni migración.
- Cada insignia trae la fecha del partido o check-in que la completó, o su avance ("3/10").
- Jugador: Debut, 10 partidos, 50 partidos, Goleador (10 goles), Triplete (3 en un partido), 10 victorias, Puntual (5 check-ins), Campeón de copa (en la planilla de la final ganada).
- Equipo: Primera victoria, 10 victorias, 25 partidos, Invicto (5 seguidos sin perder), Campeón de copa.
- Públicas como la ficha del jugador y el equipo. Nada de sanciones ni de monedas.

## Tareas

- [x] `domain/achievement_rules.py` y pruebas.
- [x] `services/achievement_queries.py` y pruebas con una copa real.
- [x] Rutas `GET /players/{id}/badges`, `GET /teams/{id}/badges`.
- [x] App: pantalla de insignias desde la ficha del jugador y desde el equipo.
- [x] Verificar en SQLite y PostgreSQL; `docs/sprint-17.md`.
