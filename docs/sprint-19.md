# Sprint 19 — Alineación táctica

- **Fecha:** 24/11/2026
- **Meta (PO):** que el DT arme la alineación antes del partido (P2 del Sprint 0: "alineaciones tácticas avanzadas") sin que el rival la vea.
- **Estado:** Verificado en SQLite y en PostgreSQL 16 local (pruebas completas, concurrencia y migración `0008`). Pendiente: emulador o teléfono y revisión independiente. El `npm test` del CI sigue aparte por decisión del dueño.

## Historias cubiertas

| Tema | Estado |
| --- | --- |
| Formación (fútbol y microfútbol) con sugerencias por modalidad | Verificado |
| Titulares exactos con posición y suplentes | Verificado |
| Solo convocados que van; se marca a quien después dice que no | Verificado |
| Solo la ve el propio equipo (y quien juega prestado ese partido) | Verificado |

## Decisiones

- **Distinta de la planilla del Sprint 7:** la planilla registra después quién jugó y los goles; la alineación táctica es el plan de antes del partido.
- **Titulares exactos** según `players_per_side` del catálogo de modalidades, cada uno con su posición (texto libre de 1 a 20 caracteres, porque cada deporte las nombra distinto). Hasta 12 suplentes.
- **Formación** solo en fútbol y microfútbol: sus líneas (de 1 a 9 cada una) suman los jugadores de campo, sin el arquero. Sugerencias: F5 y micro 2-2 y 1-2-1; F7 2-3-1, 3-2-1 y 3-3; F8 3-3-1, 3-2-2 y 2-3-2; F11 4-4-2, 4-3-3 y 3-5-2. En otros deportes no hay formación, solo posiciones.
- **Quién entra:** solo convocados que dijeron que van. Si alguien luego dice que no va, sigue en la alineación marcado como "ya no va", para que el DT decida, en lugar de desaparecer en silencio.
- **Quién la ve:** los miembros del equipo y quien juega prestado ese partido para ese equipo. El rival recibe la de su propio equipo (vacía si no la armó), nunca la ajena; un tercero recibe 404.
- **Quién la edita:** el administrador del equipo, antes de la hora del partido.
- **Privacidad de la táctica:** el evento de auditoría `TACTICS_SET` guarda solo cuántos titulares y suplentes hay, no la formación ni los nombres, porque la actividad del contrato la ven los dos equipos.
- **Convención:** la ruta para guardar es `POST` (el proyecto solo usa GET y POST en CORS y en la app).
- Migración `0008` (2 tablas).

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET | `/api/v1/contracts/{id}/tactics` | Miembros del equipo (y prestados de ese partido); cada uno ve la de su equipo |
| POST | `/api/v1/contracts/{id}/tactics` (`formation`, `starters`, `subs`) | Administrador del equipo, antes del partido |

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 324 aprobadas, 10 omitidas (las de PostgreSQL); 7 nuevas |
| `pytest` completo en PostgreSQL 16 local | 334 aprobadas, 0 omitidas |
| Migraciones `0001` → `0008`, `alembic check`, bajar a `0007` en PostgreSQL | Sin diferencias ni errores |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 51 aprobadas (3 nuevas) |
| Pruebas de componentes (`jest`) | 47 aprobadas (2 nuevas) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| ALTO | El evento de auditoría llevaba la formación, y la actividad del contrato la ven los dos equipos: el rival habría visto la táctica | El evento guarda solo conteos; prueba incluida |
| BAJO | La ruta para guardar era `PUT`, que la app y CORS no usan | Pasó a `POST`, como el resto del proyecto |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| BAJO | No hay vista gráfica de la cancha con los jugadores | Si el piloto la pide |
| BAJO | No se compara la alineación con la planilla después del partido | Posible estadística futura (titular vs. suplente) |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m alembic upgrade head
cd mobile; npx tsc --noEmit; npm test
```
