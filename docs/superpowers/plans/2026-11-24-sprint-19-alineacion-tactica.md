# Sprint 19 — Alineación táctica (plan)

**Meta:** que el DT arme la alineación antes del partido (P2 del Sprint 0: "alineaciones tácticas avanzadas"), sin que el rival la vea.

## Reglas

- Titulares exactos según la modalidad del catálogo (`players_per_side`), cada uno con su posición (1 a 20 caracteres), y hasta 12 suplentes.
- Formación solo en fútbol y microfútbol: sus líneas suman los jugadores de campo, sin el arquero (2-3-1 en fútbol 7). Sugerencias por modalidad.
- Solo entran convocados que dijeron que van (Sprint 10). Si alguien luego dice que no va, la alineación lo marca.
- La arma el administrador del equipo antes de la hora del partido. La ven los miembros del equipo y quien juega prestado ese partido; el rival nunca.
- La auditoría (`TACTICS_SET`) guarda solo conteos: la actividad del contrato la ven los dos equipos.

## Tareas

- [x] `domain/tactics_rules.py` y pruebas.
- [x] `models_tactics.py`, migración `0008`, `SportCatalog.players_per_side`.
- [x] `services/tactics_service.py`, rutas `GET|POST /contracts/{id}/tactics` y pruebas.
- [x] App: "Alineación táctica" en el contrato, con formación, titulares con posición y suplentes.
- [x] Verificar en SQLite y PostgreSQL; `docs/sprint-19.md`.
