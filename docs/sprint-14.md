# Sprint 14 — Chat del partido

- **Fecha:** 24/11/2026
- **Meta (PO):** que quienes juegan o pitan un partido lo coordinen dentro de RIVAL (P1 del Sprint 0: "chat del partido, solo participantes"), sin exponer nada a terceros.
- **Estado:** Verificado en SQLite y en PostgreSQL 16 local (pruebas completas, concurrencia y migración `0005`). Pendiente: emulador o teléfono, revisión independiente y revisión legal de la conservación de mensajes borrados.

## Historias cubiertas

| Tema | Estado |
| --- | --- |
| Chat del partido solo para participantes | Verificado |
| El árbitro asignado entra al chat desde "Mis partidos como árbitro" | Verificado |
| Borrar un mensaje propio | Verificado |
| Moderación del chat con un reporte abierto | Verificado |
| Avisos de mensajes nuevos (push o contador de no leídos) | No incluido (ver riesgos) |

## Decisiones

- **Participantes:** miembros de los dos equipos, jugadores prestados activos para ese partido y el árbitro asignado (pendiente o aceptado). Para cualquier otra persona el partido "no existe" (404), igual que el contrato.
- **Mensajes:** de 1 a 500 caracteres (los espacios repetidos se juntan); máximo 10 por persona por minuto en el mismo partido. Se escribe hasta 48 horas después de la hora del partido; un partido cancelado queda de solo lectura.
- **Sin WebSockets por ahora:** la app consulta cada 10 segundos solo los mensajes nuevos (`after_id`). Evita montar Redis y conexiones abiertas antes del piloto. [INFERENCIA] Con pocos partidos activos el costo es bajo; se revisa con datos del piloto.
- **Borrar:** solo el autor. Los participantes ven "Mensaje eliminado". [SUPUESTO] El texto se conserva para moderación; falta revisión legal (Ley 1581) [POR VERIFICAR].
- **Moderación:** una persona moderadora lee el chat completo, incluido lo borrado, solo si hay un reporte abierto sobre ese partido, y nunca si participa del partido o está involucrada en esos reportes. Cada revisión queda en la auditoría del partido (`CHAT_READ_BY_MODERATOR`) y los equipos la ven en "Ver actividad".
- **Auditoría:** se registran los borrados (`CHAT_MESSAGE_DELETED`, sin el texto) y las revisiones de moderación. Los mensajes no se auditan uno por uno: no son equipos, solicitudes, contratos, resultados ni traspasos.
- **App:** los accesos del día del partido (chat, convocatoria, préstamos, valorar) pasan como un solo objeto `matchday` al contrato, para que `ContractScreen.tsx` no pase de 150 líneas.
- Migración `0005` (1 tabla).

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET | `/api/v1/contracts/{id}/chat?after_id=` | Participantes |
| POST | `/api/v1/contracts/{id}/chat` | Participantes, con el chat abierto |
| POST | `/api/v1/chat/{id}/delete` | Autor del mensaje |
| GET | `/api/v1/moderation/contracts/{id}/chat` | Moderación, con un reporte abierto y sin conflicto de interés |

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 287 aprobadas, 10 omitidas (las de PostgreSQL); 6 nuevas |
| `pytest` completo en PostgreSQL 16 local | 297 aprobadas, 0 omitidas |
| Migraciones `0001` → `0005`, `alembic check`, bajar a `0004` y a `base` en PostgreSQL | Sin diferencias ni errores |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 43 aprobadas (3 nuevas) |
| Pruebas de componentes (`jest`) | 37 aprobadas (2 nuevas) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| CI del Sprint 13 en GitHub (Node 22.15) | Todo en verde, incluido `npm test`: el riesgo ALTO de los Sprints 10 a 13 queda cerrado |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| MEDIO | Dos consultas del chat que se cruzaban podían deshacer un borrado recién hecho en pantalla | La unión de mensajes usa el estado más reciente, no el de cuando empezó la consulta |
| BAJO | Un `except Exception` amplio para saber si el chat estaba abierto | La regla devuelve el motivo de cierre (`closed_reason`) en lugar de lanzar y atrapar |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | Nadie se entera de un mensaje nuevo si no abre el chat | Notificaciones push (decidir proveedor) o contador de no leídos |
| MEDIO | Conservar el texto borrado para moderación sin revisión legal [POR VERIFICAR] | Revisión con abogado; definir plazo de borrado definitivo |
| BAJO | Un borrado hecho por otra persona se ve al volver a abrir el chat, no en la consulta periódica | Si el piloto lo pide, traer también los cambios recientes |
| BAJO | Sin pantalla de moderación para leer el chat (solo la API) | Agregarla a la cola de reportes |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m alembic upgrade head
cd mobile; npx tsc --noEmit; npm test
```
