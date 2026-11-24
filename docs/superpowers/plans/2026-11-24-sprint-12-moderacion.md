# Sprint 12 — Moderación y confianza — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** reportes por agresión, inasistencia o perfil falso; bloqueo entre equipos; sanciones aplicadas por una persona con motivo y con apelación (Sprint 0, sección 4.8).

## Reglas

- **Moderadores:** tabla propia, no un rol de registro. Se nombran solo con `python -m app.tools.grant_moderator correo` (queda en la auditoría). Nadie se nombra moderador desde la app.
- **Reportes:** cualquier usuario reporta a otra persona o a un equipo, con categoría (AGGRESSION, NO_SHOW, FAKE_PROFILE, OTHER), descripción de 10 a 500 caracteres y, opcional, el partido. No a sí mismo ni a su propio equipo. Máximo 5 reportes por persona en 24 horas.
- **Decisión del moderador:** descartar, o sancionar con motivo: advertencia o suspensión de 1 a 30 días. Si el reporte es contra un equipo, se sanciona a su administrador actual [SUPUESTO]. El moderador no decide reportes hechos por él ni contra él.
- **Suspensión:** la persona puede entrar, ver la app y apelar, pero no hacer acciones (cualquier petición que no sea de lectura responde 403 `ACCOUNT_SUSPENDED`), hasta que termine o la revoquen.
- **Apelación:** una por sanción, dentro de 14 días, con texto. La decide un moderador distinto del que sancionó (cuatro ojos): confirma o revoca. Revocar levanta la suspensión.
- **Bloqueo:** el administrador de un equipo bloquea a otro equipo; mientras dure, ninguno ve al otro en rivales ni en búsquedas de partido, ni puede retarlo u ofertarle. Se puede desbloquear.
- Auditoría de todo. Centro de salud: sanción cuya apelación la decidió el mismo moderador que sancionó (S0).

## Tareas

- [x] Dominio `moderation_rules.py` y persistencia `models_moderation.py` + migración `0003`.
- [x] Servicios `report_service.py`, `sanction_service.py`, `block_service.py`; bloqueo en rivales, búsquedas, retos y ofertas; herramienta `grant_moderator`.
- [x] Guardia de suspensión en el usuario actual; API y pruebas.
- [x] App: reportar jugador o equipo, bloquear y desbloquear, cola del moderador, mis sanciones y apelación.
- [x] Verificación y `docs/sprint-12.md`.
- [ ] Revisión independiente y legal (pendiente).
