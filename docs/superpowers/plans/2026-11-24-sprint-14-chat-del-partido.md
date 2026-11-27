# Sprint 14 — Chat del partido (plan)

**Meta:** que quienes juegan o pitan un partido puedan coordinarlo dentro de RIVAL (P1 del Sprint 0: "chat del partido, solo participantes"), sin exponer datos a terceros.

**Arquitectura:** tabla `match_chat_message` por contrato; servicio con reglas de participantes, ventana y límite de mensajes; la app consulta cada 10 s (sin WebSockets por ahora).

## Reglas

- Participantes: miembros de los dos equipos, jugadores prestados activos para ese partido y el árbitro asignado (pendiente o aceptado). A cualquier otra persona el partido "no existe" (404).
- Mensaje: de 1 a 500 caracteres; los espacios repetidos se juntan. Máximo 10 mensajes por persona por minuto en el mismo partido.
- Se escribe hasta 48 h después de la hora del partido; un partido cancelado queda de solo lectura.
- El autor borra su mensaje: los participantes ven "Mensaje eliminado". [SUPUESTO] El texto se conserva para moderación.
- Moderación: una persona moderadora lee el chat completo (incluido lo borrado) solo si hay un reporte abierto sobre ese partido, y nunca si está involucrada.
- Auditoría: el borrado queda registrado (`CHAT_MESSAGE_DELETED`, sin el texto).

## Tareas

- [x] `domain/chat_rules.py`: texto, ventana, límite.
- [x] `persistence/models_chat.py` y migración `0005`.
- [x] `services/chat_service.py` (participantes, enviar, borrar, leer) y lectura para moderación.
- [x] `api/routes_chat.py`: `GET|POST /contracts/{id}/chat`, `POST /chat/{id}/delete`, `GET /moderation/contracts/{id}/chat`.
- [x] Pruebas de servicio y de API.
- [x] App: modelos, API, controlador con consulta cada 10 s, pantalla del chat, botón en el contrato.
- [x] Pruebas de la app, tsc, prettier, 150 líneas.
- [x] Verificar en SQLite y PostgreSQL; `docs/sprint-14.md`.
