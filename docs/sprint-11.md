# Sprint 11 — Pendientes y rivales de nivel parecido

- **Fecha:** 24/11/2026
- **Meta (PO):** que nadie se entere tarde de lo que le toca: una bandeja "Pendientes" en el inicio reúne lo que espera la acción del usuario; y al buscar rival, el DT ordena por nivel parecido.
- **Estado:** Verificado en SQLite. Pendiente: correr esta rama en PostgreSQL (las consultas son de lectura, riesgo bajo), emulador o teléfono, revisión independiente y el `npm test` en rojo del CI.

## Riesgos que cierra

| De | Riesgo | Estado |
| --- | --- | --- |
| Sprints 4, 7 y 10 | "La app no avisa" (ofertas de traspaso, convocatorias, cosas por firmar) | Mitigado: bandeja de pendientes en el inicio (sin notificaciones push todavía) |
| Sprint 10 | "El nivel solo se muestra; no ordena la búsqueda de rivales" | Cerrado: orden "Nivel parecido" |

## Decisiones

- **Pendientes calculados en cada consulta**, sin tablas ni copias: nunca quedan desactualizados. Tipos: firmar contrato, reportar marcador, marcador en disputa, convocatoria sin responder, oferta de traspaso (jugador y DT dueño), solicitudes de unión, asignación y resultado de árbitro, reserva por confirmar (dueño de establecimiento), solicitudes de liga (personal) y valorar compañeros (7 días).
- Solo aparece lo que el usuario puede hacer y aún está a tiempo (por ejemplo, firmar antes de la hora; el coordinador arbitral no ve solicitudes de equipos).
- Orden: lo que tiene hora más cercana primero. La app marca "Urgente" lo que es de un partido en menos de 24 h o ya jugado.
- Cada pendiente trae destino e id; la app abre la pantalla donde se resuelve (contrato, equipo, liga, establecimiento, ofertas de traspaso o partidos del árbitro).
- **Nivel parecido:** `order=level` en `/teams/{id}/rivals`: primero el nivel Glicko-2 más cercano al del propio equipo (1500 si aún no tiene); los equipos sin nivel, al final.
- [SUPUESTO] Sin notificaciones push en este Sprint: requieren cuentas de Expo/Firebase y aceptar sus términos, una decisión del dueño.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET | `/api/v1/me/pending` | El usuario |
| GET | `/api/v1/teams/{id}/rivals?order=level` | Miembros del equipo (antes ya existía la ruta; nuevo parámetro) |

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 267 aprobadas, 10 omitidas (las de PostgreSQL); 6 nuevas |
| `pytest` en PostgreSQL | NO EJECUTADO en esta rama (sin cambios de escritura ni de esquema) |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 34 aprobadas (2 nuevas) |
| Pruebas de componentes (`jest`) | 28 aprobadas (2 nuevas: bandeja y destinos) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| BAJO | El pendiente de reserva mostraba la hora en UTC como texto | Se manda la hora aparte y la app la muestra en hora de Colombia |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| ALTO | `npm test` falla en el CI de GitHub (Linux) | Leer el registro con sesión iniciada y corregir |
| MEDIO | Los pendientes se calculan con varias consultas por partido: con muchos partidos será lento | Medir en el piloto; si hace falta, consultas agregadas o caché corta |
| MEDIO | Sin notificaciones push | Decidir proveedor (Expo Push) y sus términos |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd mobile; npm run typecheck; npm test
```
