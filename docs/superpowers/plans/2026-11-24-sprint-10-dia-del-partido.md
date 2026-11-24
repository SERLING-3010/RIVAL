# Sprint 10 — Día del partido: convocatoria, valoraciones y nivel Glicko-2 — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** antes del partido el DT convoca y cada jugador confirma si va; después, los compañeros y el DT valoran a quienes jugaron; y cada equipo tiene un nivel (Glicko-2) que sale de sus resultados confirmados y se ve al buscar rival.

**Spec:** documento del Sprint 0, secciones 4.2.2 (valoración y convocatoria), 4.7 y 5.3; ADR-005.

## Reglas

- **Nivel Glicko-2:** por equipo; empieza en 1500, RD 350, volatilidad 0,06, τ = 0,5. [SUPUESTO] Cada resultado confirmado (por ambos equipos o por el árbitro) es un periodo de un solo partido y actualiza a los dos equipos al momento. Se muestra el nivel y qué tan confiable es (RD).
- **Convocatoria:** el administrador convoca a miembros de su equipo para un partido no cancelado y antes de la hora; cada convocado responde "voy" o "no voy" y puede cambiar su respuesta hasta la hora. El equipo ve cuántos van.
- **Valoraciones:** con resultado confirmado y planilla, cualquier miembro del equipo valora de 1 a 10 a los compañeros que jugaron (no a sí mismo), una vez por partido y compañero, hasta 7 días después de la hora. La ficha muestra el promedio y el número de votos.
- Auditoría de convocatoria, respuestas y valoraciones (sin la nota en la actividad del equipo para no exponer quién votó qué: [SUPUESTO] la nota individual es privada; solo se publica el promedio).

## Tareas

- [x] Dominio `glicko2.py` (verificado con el ejemplo del artículo de Glickman) y `matchday_rules.py`.
- [x] Persistencia `models_matchday.py`: `team_rating`, `call_up`, `player_rating`.
- [x] Servicios: `settlement_service.py` (monedas + nivel al confirmar), `callup_service.py`, `player_rating_service.py`; nivel en la búsqueda de rivales y valoración en la ficha.
- [x] API y pruebas.
- [x] App: convocatoria en el contrato, "Mis convocatorias", valorar compañeros, nivel del equipo.
- [x] Verificación y `docs/sprint-10.md`.
- [ ] Revisión independiente (pendiente).
