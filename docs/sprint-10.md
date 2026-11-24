# Sprint 10 — Día del partido: convocatoria, valoraciones y nivel Glicko-2

- **Fecha:** 24/11/2026
- **Meta (PO):** que el antes y el después del partido vivan en la app: el DT convoca y los jugadores confirman; los compañeros se valoran; cada equipo tiene un nivel que sale de sus resultados reales y se ve al buscar rival.
- **Estado:** Verificado en SQLite y en PostgreSQL 16 local (pruebas de concurrencia y del día del partido). Pendiente: emulador o teléfono, revisión independiente y el fallo de `npm test` en el CI del Sprint 9 (aparcado por decisión del dueño).

## Historias y pendientes cubiertos

| Tema (Sprint 0) | Estado |
| --- | --- |
| 4.2.2 Convocatoria: "el jugador confirma si va" | Verificado |
| 4.2.2 Valoración de compañeros con número de votos visible | Verificado |
| 5.3 / ADR-005: nivel Glicko-2 por equipo | Verificado; reproduce el ejemplo del artículo de Glickman (1464,06 / 151,52 / 0,05999) |
| 5.3 Fase 2: ver el nivel al buscar rival | Verificado: nivel y si ya es confiable en la búsqueda de rivales |

## Decisiones

- **Glicko-2:** 1500 / RD 350 / volatilidad 0,06 / τ 0,5 al empezar. [SUPUESTO] Cada resultado confirmado (por los dos equipos o por el árbitro) es un periodo de un solo partido y actualiza a ambos equipos al momento. [SUPUESTO] El nivel se muestra como "confiable" con RD ≤ 100.
- **Liquidación única:** un solo servicio (`settlement_service`) paga las monedas y actualiza el nivel cuando un resultado queda confirmado, lo llame el reporte de los equipos o el del árbitro. Bloquea los dos equipos en orden de id, igual que un traspaso, para que no se bloqueen entre sí.
- **Convocatoria:** el administrador convoca a miembros de su equipo para un partido no cancelado y antes de la hora; cada convocado responde "voy" o "no voy" y puede cambiar hasta la hora. El equipo ve cuántos van. "Mis convocatorias" lista solo partidos futuros.
- **Valoraciones:** con resultado confirmado y planilla, cada miembro del equipo valora de 1 a 10 a los compañeros que jugaron, una vez por partido, hasta 7 días después. [SUPUESTO] La nota es privada: la auditoría registra que alguien valoró, no cuánto; la ficha solo muestra promedio y votos.
- Migración `0002` (3 tablas). La prueba de migraciones del Sprint 9 detectó las tablas sin migración antes de crearla: la protección funciona. La plantilla de migraciones ahora importa el tipo de fecha propio para que las siguientes no fallen.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET · POST | `/api/v1/contracts/{id}/callup` | Miembros de un equipo del partido · su administrador |
| POST | `/api/v1/contracts/{id}/callup/respond` | El convocado |
| GET | `/api/v1/me/callups` | El jugador |
| GET | `/api/v1/contracts/{id}/ratings/pending` | Miembro del equipo |
| POST | `/api/v1/contracts/{id}/ratings` | Miembro del equipo |

Además: `level` y `level_reliable` en la búsqueda de rivales; `level`, `level_rd` y `level_matches` en el modo manager; `rating_average` y `rating_votes` en la ficha del jugador.

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 261 aprobadas, 10 omitidas (las de PostgreSQL); 13 nuevas |
| Concurrencia + día del partido + árbitro en PostgreSQL 16.2 local | 20 aprobadas |
| Migraciones `0001` → `0002` en PostgreSQL y `alembic check` | Sin diferencias |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 32 aprobadas (2 nuevas) |
| Pruebas de componentes (`jest`) | 26 aprobadas (3 nuevas) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |
| CI en GitHub | NO EJECUTADO para esta rama; el del Sprint 9 tiene `npm test` en rojo sin diagnóstico (falta leer el registro con sesión iniciada) |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| MEDIO | El pago de monedas al confirmar bloqueaba los equipos local→visitante; un traspaso los bloquea por id: riesgo de bloqueo mutuo | `settlement_service` bloquea ambos en orden de id antes de pagar |
| BAJO | Las migraciones generadas no importaban el tipo `UtcDateTime` | Plantilla `script.py.mako` corregida |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| ALTO | `npm test` falla en el CI de GitHub (Linux) y pasa aquí | Leer el registro y corregir |
| MEDIO | Los valores de Glicko-2 y el umbral de "confiable" son supuestos | Ajustarlos con datos del piloto |
| MEDIO | El nivel aún no filtra ni ordena la búsqueda de rivales (solo se muestra) | Emparejamiento por nivel parecido |
| BAJO | Nadie recibe aviso de una convocatoria nueva | Notificaciones push |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; $env:RIVAL_TEST_DATABASE_URL = (.\venv\Scripts\python.exe dev_tools\local_pg.py); .\venv\Scripts\python.exe -m pytest -q
cd mobile; npm run typecheck; npm test
```
