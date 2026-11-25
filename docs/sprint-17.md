# Sprint 17 — Logros e insignias

- **Fecha:** 24/11/2026
- **Meta (PO):** reconocer a jugadores y equipos por lo que hacen en la cancha (P2 del Sprint 0: "logros e insignias"), sin dinero y sin que nadie las pueda otorgar a mano.
- **Estado:** Verificado en SQLite y en PostgreSQL 16 local (pruebas completas y `alembic check` sin diferencias). Pendiente: emulador o teléfono y revisión independiente. El `npm test` del CI sigue aparte por decisión del dueño.

## Historias cubiertas

| Tema | Estado |
| --- | --- |
| Insignias de jugador con fecha o avance | Verificado |
| Insignias de equipo con fecha o avance | Verificado |
| Pantalla de insignias desde la ficha del jugador y desde el equipo | Verificado en pruebas de componentes |

## Decisiones

- **Calculadas, no guardadas:** cada consulta las saca de datos reales (partidos con resultado confirmado, planillas, check-ins y copas). No hay tabla ni migración, así nunca quedan desactualizadas, no se pueden otorgar a mano y, si un resultado se corrige, la insignia se corrige sola.
- **Fecha:** la de confirmación del resultado (o la hora del check-in) que completó la insignia. Mientras no se gana, muestra el avance ("3/10").
- **Jugador:** Debut, 10 partidos, 50 partidos, Goleador (10 goles), Triplete (3 o más en un partido), 10 victorias, Puntual (5 check-ins) y Campeón de copa (estar en la planilla de la final ganada).
- **Equipo:** Primera victoria, 10 victorias, 25 partidos, Invicto (5 seguidos sin perder; una derrota reinicia la racha) y Campeón de copa.
- **Sin sanciones ni monedas:** no hay insignias de "juego limpio" (expondrían sanciones, que son privadas) ni que se compren. Las monedas RIVAL siguen siendo virtuales.
- [SUPUESTO] Las metas (10, 25, 50…) se ajustan con datos del piloto.
- Públicas como la ficha del jugador: cualquier usuario las ve.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET | `/api/v1/players/{id}/badges` | Cualquier usuario |
| GET | `/api/v1/teams/{id}/badges` | Cualquier usuario |

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 309 aprobadas, 10 omitidas (las de PostgreSQL); 7 nuevas |
| `pytest` completo en PostgreSQL 16 local | 319 aprobadas, 0 omitidas |
| `alembic check` en PostgreSQL (sin migración nueva) | Sin diferencias |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 47 aprobadas (1 nueva) |
| Pruebas de componentes (`jest`) | 43 aprobadas (1 nueva) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| BAJO | Las finales de copa se consultaban una vez por partido del jugador | Una consulta por equipo |
| BAJO | Funciones `lambda` con `noqa` en las reglas | Funciones con nombre, sin `noqa` |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| BAJO | Calcular en cada consulta puede ser lento con muchos partidos | Medir en el piloto; si hace falta, caché corta |
| BAJO | Nadie recibe aviso al ganar una insignia | Con las notificaciones push |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd mobile; npx tsc --noEmit; npm test
```
