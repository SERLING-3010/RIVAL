# Sprint 2 — Rivales, retos, ofertas y agentes libres — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** un DT encuentra rival por cercanía, barrio o ciudad, lo reta o publica una búsqueda abierta que recibe ofertas al estilo InDriver; los jugadores sin equipo aparecen como agentes libres y aceptan invitaciones.

**Arquitectura:** mismas capas del Sprint 1. Cercanía entre centros de barrio del catálogo (ADR-006). Pruebas en SQLite y PostgreSQL 16 + PostGIS.

**Spec:** documento del Sprint 0, secciones 4.2, 4.3, 4.4.1 y 9.3 (RIV-006, RIV-007, RIV-008).

## Restricciones globales

- Las del Sprint 1, más: nunca coordenadas en respuestas; rangos UNDER_2_KM, FROM_2_TO_5_KM, OVER_5_KM; radio entre 1 y 15 km.
- Fechas con zona horaria (AwareDatetime); la app escribe en hora de Colombia (-05:00).
- Ventana de partido: futura, máximo 14 días de duración, máximo 60 días adelante; máximo 3 búsquedas abiertas por equipo.
- Árbitro opcional: la búsqueda acepta WITH, WITHOUT o EITHER; la oferta debe concretar WITH o WITHOUT.
- Una oferta pendiente por equipo y búsqueda (índice único parcial); una contraoferta crea versión nueva.
- Aceptar bloquea la búsqueda (FOR UPDATE).
- El jugador siempre acepta la invitación; las invitaciones no aparecen como solicitudes del Sprint 1.

## Review Focus

1. Dos administradores aceptan ofertas distintas a la vez: solo una gana (prueba en PostgreSQL).
2. Un reto directo no lo ve ningún equipo distinto del retado.
3. Una búsqueda NEARBY de 2 km no la ve un equipo a 4 km aunque mire "Mi ciudad".
4. Búsqueda vencida: sale del feed y no se puede aceptar ninguna oferta.
5. Fechas sin zona horaria: la API responde 422.

## Tareas

- [x] Dominio: `geo.py`, `match_rules.py` con pruebas.
- [x] Catálogo de barrios: `models_places.py`, `neighborhood_service.py`, `tools/import_neighborhoods.py`.
- [x] Rivales: `rival_service.py`.
- [x] Agentes libres e invitaciones: `free_agent_service.py`, `invitation_service.py`.
- [x] Búsquedas y ofertas: `match_request_service.py`, `match_feed_service.py`, `match_offer_service.py`.
- [x] API: `routes_scouting.py`, `routes_matches.py` con límite de 60 búsquedas por usuario cada 10 minutos.
- [x] App: pantallas de rivales, agentes libres, búsquedas, feed, oferta y ofertas.
- [x] Verificación en SQLite y PostgreSQL, revisión independiente y entrega.
