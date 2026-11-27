# Sprint 15 — Check-in en la cancha

- **Fecha:** 24/11/2026
- **Meta (PO):** saber quién llegó a un partido (último P1 del Sprint 0: "el check-in compara la distancia al establecimiento y guarda solo llegó / no llegó"), sin guardar la posición de nadie.
- **Estado:** Verificado en SQLite y en PostgreSQL 16 local (pruebas completas, concurrencia y migración `0006`). Pendiente: probar el GPS en un teléfono real (emulador o dispositivo), revisión independiente, revisión legal del texto del permiso y el `npm test` del CI del Sprint 14.

## Decisión del dueño (24/11/2026)

GPS una sola vez, mientras se usa la app, con `expo-location` (paquete oficial de Expo, instalado con `npx expo install`). El servidor compara y descarta la posición.

## Historias cubiertas

| Tema | Estado |
| --- | --- |
| El dueño guarda la ubicación de su establecimiento, desde el lugar | Verificado |
| Check-in "Llegué" desde el contrato, con la posición de una sola lectura | Verificado en pruebas; GPS real NO EJECUTADO |
| Lista de quién llegó y a qué hora, para los participantes | Verificado |
| "No llegó" como evidencia para un reporte de inasistencia | Parcial: se ve quién no aparece en la lista; no se marca solo |

## Decisiones

- **Ubicación del establecimiento:** es la de un negocio, que ya muestra su dirección (ADR-004). La fija su dueño estando en la cancha y no se muestra a los jugadores. Se guarda redondeada a 6 decimales.
- **Posición de las personas:** viaja una vez en el cuerpo de la petición, se compara con la cancha y se descarta. No hay columna para ella (`match_check_in` solo tiene contrato, persona y hora), no va a la auditoría (`CHECKED_IN` guarda solo quién) y los registros de errores no incluyen el cuerpo de las peticiones. Una prueba lo comprueba.
- **Permiso:** solo "mientras se usa la app" en Android e iOS; la ubicación en segundo plano está apagada en `app.json` y la configuración generada solo pide `ACCESS_FINE_LOCATION` y `ACCESS_COARSE_LOCATION`.
- **Cuándo:** solo en partidos con reserva confirmada en una cancha que tenga ubicación; desde 60 minutos antes de la hora hasta que termina el partido (hora + duración).
- **Quién:** los participantes del partido (los mismos del chat; la regla vive ahora en `match_participants.py`).
- [SUPUESTO] **Llegó** = a 250 m o menos de la cancha, como margen para el error del GPS. Se ajusta con el piloto.
- Un check-in por persona y partido (restricción única); repetirlo no cambia la hora.
- Migración `0006` (1 tabla y 2 columnas en `venue`).

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET | `/api/v1/contracts/{id}/check-ins` | Participantes |
| POST | `/api/v1/contracts/{id}/check-ins` (`latitude`, `longitude`) | Participantes, en la ventana y a 250 m o menos |
| POST | `/api/v1/venues/{id}/location` (`latitude`, `longitude`) | Dueño del establecimiento |

`GET /api/v1/venues/{id}` ahora incluye `has_location`.

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 292 aprobadas, 10 omitidas (las de PostgreSQL); 5 nuevas |
| `pytest` completo en PostgreSQL 16 local | 302 aprobadas, 0 omitidas |
| Migraciones `0001` → `0006`, `alembic check`, bajar a `0005` y a `base` en PostgreSQL | Sin diferencias ni errores |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 44 aprobadas (1 nueva) |
| Pruebas de componentes (`jest`) | 40 aprobadas (3 nuevas) |
| Mismas pruebas con `CI=true TZ=UTC LANG=C` | Aprobadas |
| `expo config`: permisos de ubicación | Solo primer plano |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| GPS en teléfono o emulador | NO EJECUTADO |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| MEDIO | La regla de participantes estaba dentro del chat y el check-in la necesitaba igual | Se movió a `match_participants.py`, usada por los dos |
| BAJO | La prueba "solo con cancha confirmada" no probaba un partido sin cancha | Se agregó el caso: sin reserva no hay check-in (`NO_CONFIRMED_VENUE`) |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| ALTO | `npm test` falló en el CI del Sprint 14 (pasa aquí, también con `CI=true TZ=UTC`); los registros piden iniciar sesión en GitHub [POR VERIFICAR] | Leer el registro con sesión iniciada |
| MEDIO | Un teléfono puede falsear su GPS | Es evidencia, no prueba: el árbitro y los reportes siguen decidiendo |
| MEDIO | Texto del permiso sin revisión legal (Ley 1581) [POR VERIFICAR] | Revisión con abogado antes del piloto |
| BAJO | El radio de 250 m es un supuesto | Ajustar con datos del piloto |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m alembic upgrade head
cd mobile; npx tsc --noEmit; npm test
```
