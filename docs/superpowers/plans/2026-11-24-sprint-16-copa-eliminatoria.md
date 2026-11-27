# Sprint 16 — Copa eliminatoria de liga (plan)

**Meta:** que una liga pueda jugar una copa por eliminación directa (P2 del Sprint 0: "torneos eliminatorios"), reutilizando contratos, árbitros y resultados.

## Reglas

- Una copa por liga; la arma el organizador o un coorganizador con los equipos aprobados (2 a 32).
- Siembra por nivel Glicko-2 (sin partidos, 1500; a igual nivel, el inscrito primero). Cuadro clásico: el 1 contra el último.
- Si no son potencia de 2, los mejores sembrados pasan directo la primera ronda.
- Cada cruce con sus dos equipos nace como contrato de la liga (árbitro y lugar por acordar), como el calendario.
- El resultado confirmado (por los admins o por el árbitro) hace avanzar al ganador; el cruce siguiente nace cuando tiene sus dos equipos.
- [SUPUESTO] Empate: lo define el organizador por penales, con auditoría. Si la fecha de una ronda ya pasó, el cruce se programa al día siguiente a la misma hora.
- La copa no suma a la tabla de la liga: la tabla cuenta solo los partidos del calendario.

## Tareas

- [x] `domain/cup_rules.py` y pruebas.
- [x] `models_cup.py`, migración `0007`.
- [x] `cup_service` (armar, penales), `cup_advance` (avance desde el resultado), `cup_queries` (cuadro).
- [x] Tabla de la liga solo con el calendario.
- [x] Rutas `GET|POST /leagues/{id}/cup`, `POST /cup-matches/{id}/tiebreak` y pruebas.
- [x] App: pantalla de la copa, botón en la liga, penales para el organizador.
- [x] Verificar en SQLite y PostgreSQL; `docs/sprint-16.md`.
