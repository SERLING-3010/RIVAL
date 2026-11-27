# Sprint 18 — Rivales sugeridos con motivos

- **Fecha:** 24/11/2026
- **Meta (PO):** sugerir rivales y decir por qué (P2 del Sprint 0: "sugerencias explicables: te sugerimos a X porque está cerca, juega los sábados y su nivel es parecido; nunca sanciones automáticas").
- **Estado:** Verificado en SQLite y en PostgreSQL 16 local (pruebas completas y `alembic check` sin diferencias). Pendiente: emulador o teléfono y revisión independiente. El `npm test` del CI sigue aparte por decisión del dueño.

## Historias cubiertas

| Tema | Estado |
| --- | --- |
| Rivales sugeridos con sus motivos | Verificado |
| Sin bloqueados, sin rivales recientes ni ya pactados | Verificado |
| "Retar" desde la sugerencia (administrador) | Verificado en pruebas de componentes |

## Decisiones

- **Reglas a la vista, no un modelo opaco:** cada punto tiene su motivo escrito. No se usa un servicio externo de IA ni se envían datos a terceros. [INFERENCIA] Para el piloto esto basta; un modelo aprendido solo tendría sentido con muchos datos y seguiría teniendo que explicar cada sugerencia.
- **Candidatos:** mismo deporte, modalidad y ciudad; sin equipos bloqueados en ninguna dirección.
- **Puntos:** cercanía entre centros de barrio por rangos (menos de 2 km: 3; de 2 a 5 km: 2), nivel Glicko-2 parecido (diferencia de hasta 100: 3; hasta 200: 1), mismo día favorito de juego (2) y no haberse enfrentado en el último mes (1).
- **Día favorito:** el día de la semana más frecuente entre los últimos 10 partidos firmados de cada equipo, en hora de Colombia [SUPUESTO: piloto en Colombia].
- **No se sugiere** a quien ya se enfrentó en los últimos 30 días ni a quien ya tiene partido pactado.
- **Máximo 5**, y solo con al menos un motivo fuerte (cercanía, nivel o día), no solo "no se han enfrentado".
- **Privacidad (ADR-004):** la cercanía siempre en rangos; nunca kilómetros exactos ni coordenadas. Solo lo ven los miembros del equipo.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET | `/api/v1/teams/{id}/suggestions` | Miembros del equipo |

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 317 aprobadas, 10 omitidas (las de PostgreSQL); 8 nuevas |
| `pytest` completo en PostgreSQL 16 local | 327 aprobadas, 0 omitidas |
| `alembic check` en PostgreSQL (sin migración nueva) | Sin diferencias |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 48 aprobadas (1 nueva) |
| Pruebas de componentes (`jest`) | 45 aprobadas (2 nuevas) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| MEDIO | Un rival ya pactado seguía apareciendo: el partido pactado hacía que ambos "jugaran el mismo día" y compensaba la penalización | Quien se enfrentó en el último mes o ya tiene partido pactado queda fuera de las sugerencias |
| BAJO | Dos líneas pasaban de 120 caracteres | Partidas |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| BAJO | Los pesos de cada motivo son supuestos | Ajustarlos con lo que acepten los equipos en el piloto |
| BAJO | Se calcula en cada consulta | Medir en el piloto; si hace falta, caché corta |
| BAJO | No sugiere agentes libres a equipos cortos de jugadores | Siguiente paso posible de este mismo módulo |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd mobile; npx tsc --noEmit; npm test
```
