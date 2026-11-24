# Sprint 5 — Ligas y cuerpo arbitral — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** un jugador o DT con equipo, o un árbitro, crea una liga y queda como organizador; los equipos piden inscribirse y los árbitros piden entrar al cuerpo arbitral; el organizador (o quien él nombre) aprueba o rechaza.

**Spec:** documento del Sprint 0, secciones 4.2.1, 4.5, 6.1 y 9.3 (RIV-010, RIV-011).

## Reglas

- Crea una liga: quien tiene el rol de árbitro o es miembro de un equipo activo. Queda como ORGANIZER.
- La liga tiene nombre (3–60), deporte y modalidad del catálogo, ciudad, temporada (`2026` o `2026-1`/`2026-2`) y descripción opcional.
- Personal: ORGANIZER, CO_ORGANIZER, REFEREE_COORDINATOR. Solo un ORGANIZER nombra personal; nombrar a alguien exige que la cuenta exista. Siempre queda al menos un organizador (no se quita personal en este Sprint).
- Inscripción de equipo: la pide el administrador del equipo; deporte, modalidad y ciudad iguales a los de la liga. Aprueban ORGANIZER o CO_ORGANIZER.
- Cuerpo arbitral: lo pide una cuenta con rol de árbitro y el deporte de la liga entre sus deportes. Aprueban ORGANIZER, CO_ORGANIZER o REFEREE_COORDINATOR.
- Una solicitud pendiente o aprobada por equipo/árbitro y liga (índice único parcial). Quien pidió puede retirar la pendiente; un aprobado puede salir.
- Solo el personal ve las solicitudes pendientes; cualquiera ve la liga con equipos y árbitros aprobados.
- Todo queda en la auditoría.

## [SUPUESTO] Fuera de este Sprint

- Calendario, tabla de posiciones, canchas sede, decisiones con dos organizadores, voto si el organizador abandona.
- Asignar árbitros a partidos y que el árbitro confirme resultados.

## Tareas

- [x] Dominio `league_rules.py` con pruebas.
- [x] Persistencia `models_leagues.py`.
- [x] Servicios `league_service.py`, `league_enrollment_service.py`, `league_views.py`.
- [x] API `routes_leagues.py`, `schemas_leagues.py`.
- [x] App: buscar y crear liga, detalle con inscripción, cuerpo arbitral y decisiones del personal.
- [x] Verificación y `docs/sprint-05.md`.
- [ ] Revisión independiente y prueba en PostgreSQL (pendientes).
