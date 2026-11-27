# Sprint 18 — Rivales sugeridos con motivos (plan)

**Meta:** sugerir rivales y decir por qué (P2 del Sprint 0: "sugerencias explicables... nunca sanciones automáticas"), sin mostrar ubicaciones exactas.

## Reglas

- Candidatos: mismo deporte, modalidad y ciudad; sin equipos bloqueados en ninguna dirección.
- Motivos y puntos: cercanía por rangos entre centros de barrio (menos de 2 km: 3; de 2 a 5 km: 2), nivel Glicko-2 parecido (hasta 100: 3; hasta 200: 1), mismo día favorito de juego en hora de Colombia (2) y no haberse enfrentado en el último mes (1).
- No se sugiere a quien ya se enfrentó en los últimos 30 días ni a quien ya tiene partido pactado.
- Se muestran hasta 5, con al menos un motivo fuerte. Reglas a la vista, sin servicio externo de IA y sin enviar datos a terceros.

## Tareas

- [x] `domain/suggestion_rules.py` y pruebas.
- [x] `services/suggestion_service.py`, ruta `GET /teams/{id}/suggestions` y pruebas.
- [x] App: "Rivales sugeridos" en el equipo, con motivos y "Retar" para el administrador.
- [x] Verificar en SQLite y PostgreSQL; `docs/sprint-18.md`.
