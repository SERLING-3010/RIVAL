# Sprint 15 — Check-in en la cancha (plan)

**Meta:** saber quién llegó al partido (P1 del Sprint 0: "el check-in compara la distancia al establecimiento y guarda solo llegó / no llegó"), sin guardar la posición de nadie.

**Decisión del dueño (24/11/2026):** GPS una sola vez, mientras se usa la app, con `expo-location`.

## Reglas

- La cancha guarda su ubicación (es un negocio y ya muestra su dirección): su dueño la fija una vez desde el lugar.
- Solo hay check-in en partidos con reserva confirmada en una cancha que tenga ubicación.
- Hacen check-in los participantes del partido (los mismos del chat), desde 60 min antes de la hora hasta que termina el partido.
- El servidor compara la posición con la de la cancha y la descarta: no se guarda, no se registra y no viaja a la auditoría. Se guarda solo "llegó" y la hora.
- [SUPUESTO] Llegó = a 250 m o menos de la cancha (margen para el error del GPS).
- Un check-in por persona y partido (índice único); repetirlo no cambia la hora.
- Auditoría: `CHECKED_IN` (sin coordenadas) y `VENUE_LOCATION_SET`.

## Tareas

- [x] `domain/checkin_rules.py`: ventana, radio.
- [x] `Venue.latitude/longitude`, tabla `match_check_in`, migración `0006`.
- [x] `services/checkin_service.py`, ubicación de la cancha en `venue_service`.
- [x] Rutas: `GET|POST /contracts/{id}/check-ins`, `POST /venues/{id}/location`.
- [x] Pruebas de servicio y de API.
- [x] App: `expo-location`, permiso en `app.json`, pantalla de check-in, botón en el contrato, "Guardar ubicación" para el dueño de la cancha.
- [x] Pruebas de la app, tsc, prettier, 150 líneas.
- [x] Verificar en SQLite y PostgreSQL; `docs/sprint-15.md`.
