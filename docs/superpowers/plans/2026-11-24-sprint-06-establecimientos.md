# Sprint 6 — Establecimientos, canchas y franjas — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** el dueño de un establecimiento registra sus canchas y publica franjas disponibles; el administrador de un equipo con partido firmado en "cancha de establecimiento" pide la franja que cubre la hora del partido; el establecimiento confirma o rechaza. Nunca hay dos confirmaciones para la misma franja. El contrato muestra "Listo para jugar" cuando el lugar está acordado.

**Spec:** documento del Sprint 0, secciones 4.6, 6, 6.1, 7.6 y 9.3 (RIV-012).

## Reglas

- Registra establecimientos quien tiene el rol VENUE_OWNER. Nombre 3–60, dirección 5–120 (es un negocio: la dirección es pública), barrio y ciudad, tarifa de referencia por hora opcional en pesos (decimal exacto, solo informativa: el pago es fuera de la app).
- Cancha: nombre, deporte del catálogo, superficie opcional.
- Franja: inicio futuro, como máximo 60 días adelante, duración de 30 a 240 minutos; sin traslape con otra franja de la misma cancha.
- Reserva: la pide el administrador de uno de los dos equipos de un contrato firmado, no cancelado, con lugar VENUE, antes de la hora. La franja debe contener todo el partido (inicio y duración de la versión firmada) y ser del deporte del partido.
- Una reserva activa (pendiente o confirmada) por contrato; una confirmada por franja: verificación previa, bloqueo de la franja (FOR UPDATE) e índice único parcial en la base de datos.
- Confirmar rechaza automáticamente las demás pendientes de esa franja. El dueño confirma o rechaza; quien pidió puede cancelar. Cancelar el partido cancela su reserva.
- "Listo para jugar": contrato firmado y, si el lugar es VENUE, reserva confirmada. Lugar informal o por acordar no necesitan confirmación de nadie.
- Centro de salud: dos reservas confirmadas en la misma franja (S0); reserva confirmada que ya no cubre la hora firmada (S1).

## Tareas

- [x] Dominio `venue_rules.py` con pruebas.
- [x] Persistencia `models_venues.py`.
- [x] Servicios `venue_service.py`, `venue_queries.py`, `booking_service.py`; contrato con reserva y "Listo para jugar"; chequeos de salud.
- [x] API `routes_venues.py`, `schemas_venues.py`.
- [x] App: "Mi establecimiento" (canchas, franjas, reservas por decidir) y "Reservar cancha" desde el contrato.
- [x] Verificación y `docs/sprint-06.md`.
- [ ] Revisión independiente y prueba de concurrencia en PostgreSQL (pendientes).
