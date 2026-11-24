# Sprint 13 — Modo manager 2: préstamos y ventanas de traspasos

- **Fecha:** 24/11/2026
- **Meta (PO):** que un equipo corto de jugadores pueda pedir uno prestado para un partido, siempre con la aceptación del DT dueño y del jugador, y que cada liga pueda fijar una ventana de traspasos.
- **Estado:** Verificado en SQLite y en PostgreSQL 16 local (pruebas completas, concurrencia y migración `0004`). Pendiente: emulador o teléfono, revisión independiente y confirmar en el CI que Node 22.15 arregla el `npm test`.

## Historias cubiertas

| Tema | Estado |
| --- | --- |
| Pedir un jugador prestado para un partido | Verificado |
| Aceptación en dos pasos: DT del equipo dueño y después el jugador | Verificado |
| El prestado entra en la convocatoria y la planilla de ese partido | Verificado (solo de ese partido) |
| Ventana de traspasos por liga | Verificado; fuera de ella no se oferta ni se cierra un traspaso |
| Préstamos en la bandeja de pendientes | Verificado |

## Decisiones

- **Un préstamo vale para un solo partido** (un contrato). No mueve al jugador de equipo ni usa monedas RIVAL.
- **Nadie juega prestado sin aceptarlo:** estados `PENDING_OWNER` → `PENDING_PLAYER` → `ACTIVE`. El jugador no puede decidir antes que su DT, y todo se cierra al empezar el partido.
- **Quién se presta:** solo un miembro con rol jugador (no DT ni capitán), de un equipo del mismo deporte que no juega ese partido y que no esté ya en el equipo que lo pide.
- **Un préstamo abierto por jugador y partido**, garantizado en la base con un índice único parcial (`uq_player_loan_open`).
- **Cancelar:** el jugador o el administrador de cualquiera de los dos equipos.
- **Ventana de traspasos:** la fija o la quita el organizador o un coorganizador. Si no hay ventana, los traspasos quedan abiertos (como antes). [SUPUESTO] La ventana aplica cuando alguno de los dos equipos del traspaso juega una liga con ventana cerrada.
- Todo queda en la auditoría encadenada: `LOAN_*` sobre el contrato y `TRANSFER_WINDOW_SET` sobre la liga.
- **CI:** Node fijado en `22.15.0`, la misma versión local, para descartar el fallo de `npm test` en Linux.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET · POST | `/api/v1/contracts/{id}/loans` | Administradores del partido |
| GET | `/api/v1/me/loans` | El jugador o el DT dueño que debe decidir |
| POST | `/api/v1/loans/{id}/owner-accept` · `owner-reject` | DT del equipo dueño |
| POST | `/api/v1/loans/{id}/player-accept` · `player-reject` | El jugador |
| POST | `/api/v1/loans/{id}/cancel` | El jugador o un administrador de los equipos |
| POST | `/api/v1/leagues/{id}/transfer-window` | Organizador o coorganizador |

## App

- En el contrato, el administrador ve **"Pedir jugador prestado"** antes del resultado. Elige un equipo de su ciudad y luego un jugador.
- La pantalla **Préstamos** se abre desde la bandeja de pendientes; ahí deciden el DT dueño y el jugador.
- En la liga, la tarjeta **Ventana de traspasos** muestra su estado a todos. El organizador la fija con fechas `dd/mm/aaaa hh:mm` (hora de Colombia) o la quita.

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 281 aprobadas, 10 omitidas (las de PostgreSQL); 5 nuevas |
| `pytest` completo en PostgreSQL 16 local | 291 aprobadas, 0 omitidas |
| Migraciones `0001` → `0004`, `alembic check`, bajar a `0003` y a `base` en PostgreSQL | Sin diferencias ni errores |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 40 aprobadas (3 nuevas) |
| Pruebas de componentes (`jest`) | 35 aprobadas (4 nuevas) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia

Riesgos que se cubrieron desde el diseño (no hubo defectos encontrados después de escribir el código):

| Impacto | Riesgo | Cómo se cubre |
| --- | --- | --- |
| ALTO | Que un préstamo moviera al jugador de equipo sin su aceptación | El préstamo no cambia la membresía: solo habilita al jugador en ese contrato, y exige su aceptación |
| MEDIO | Dos solicitudes simultáneas del mismo jugador para el mismo partido | Índice único parcial y bloqueo del contrato (`FOR UPDATE`) |
| BAJO | `transfer_service.py` cerca del límite de 150 líneas | La ventana vive en `transfer_window_service.py` (130 líneas el servicio de traspasos) |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| ALTO | `npm test` falla en el CI de GitHub [POR VERIFICAR] | Ver si Node 22.15 lo arregla; si no, leer el registro |
| MEDIO | La lista de equipos para pedir prestado muestra solo la primera página de la ciudad | Agregar "Ver más" si el piloto lo pide |
| BAJO | No hay límite de préstamos por equipo ni por temporada | Decidir con el dueño |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m alembic upgrade head
cd mobile; npx tsc --noEmit; npm test
```
