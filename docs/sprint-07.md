# Sprint 7 — Modo manager: fichas, monedas RIVAL y mercado de fichajes

- **Fecha:** 24/11/2026
- **Meta (PO):** que manejar el equipo se sienta como un juego de gestión con partidos y personas reales (decisión del dueño, Sprint 0, sección 4.2.2): fichas con estadísticas reales, presupuesto en monedas virtuales y un mercado de fichajes donde el jugador siempre acepta.
- **Estado:** Implementado y verificado en SQLite; pendiente de PostgreSQL (traspasos simultáneos), de la prueba en emulador o teléfono y de la revisión independiente humana.

## Historias cubiertas

| ID | Historia | Estado |
| --- | --- | --- |
| RIV-016 | Como jugador, ver mis estadísticas reales, calculadas solo de partidos con resultado confirmado | Verificado (SQLite) con planilla del partido |
| RIV-015 | Como DT, fichar jugadores con monedas virtuales: oferta → acepta el DT dueño → acepta el jugador; nunca dinero real | Verificado (SQLite) |

## Decisiones

- **Planilla del partido:** con el resultado confirmado, el administrador de cada equipo marca quién jugó (miembros actuales) y los goles de cada uno; la suma no supera el marcador. Se puede corregir y cada corrección queda en la auditoría.
- **Ficha:** partidos, goles, ganados, empatados y perdidos, solo de partidos confirmados con planilla. Nada de atributos inventados.
- **Monedas RIVAL:** enteros virtuales en un libro de movimientos (solo asientos nuevos; el saldo es la suma). El saldo nunca queda negativo: cada movimiento bloquea el equipo y revisa el saldo. No se compran ni se venden con dinero real.
- [SUPUESTO, ajustable] Presupuesto inicial 1.000 RC al crear el equipo; por partido confirmado +50 a cada equipo, +100 extra al ganador, +25 extra a cada uno en empate.
- **Mercado:** el administrador pone en el mercado a jugadores con rol PLAYER (el DT y el capitán no se transfieren). Otro administrador del mismo deporte ofrece monedas (sin superar su saldo); una oferta nueva del mismo equipo reemplaza la anterior.
- **El jugador siempre acepta:** primero decide el DT dueño y después el jugador; nadie puede aceptar por él. Solo con las dos aceptaciones, en una transacción y con los dos equipos bloqueados en orden de id: se pagan las monedas (el saldo se revisa otra vez), el jugador pasa al nuevo equipo como PLAYER, sale del mercado y se cancelan las demás ofertas por él.
- Los traspasos y movimientos de monedas aparecen en la actividad del equipo.
- Centro de salud: saldo negativo (S0) y traspaso completado sin la aceptación del jugador (S0).
- [SUPUESTO] Fuera de este Sprint: valoraciones de compañeros, préstamos por un partido, ventanas de traspasos por liga, alineación visual y convocatoria, premio por juego limpio, contraofertas del DT dueño.

## API nueva

| Método | Ruta | Quién |
| --- | --- | --- |
| GET | `/api/v1/players/{id}/card` | Cualquier usuario |
| GET | `/api/v1/teams/{id}/manager` | Miembros (ofertas solo para el administrador) |
| POST | `/api/v1/teams/{id}/transfer-list` | Administrador del equipo |
| GET | `/api/v1/market?sport=&city=` | Cualquier usuario |
| POST | `/api/v1/teams/{id}/transfer-offers` | Administrador del equipo comprador |
| POST | `/api/v1/transfer-offers/{id}/owner-accept` · `owner-reject` | Administrador del equipo dueño |
| POST | `/api/v1/transfer-offers/{id}/player-accept` · `player-reject` | Solo el jugador |
| POST | `/api/v1/transfer-offers/{id}/withdraw` | Administrador del equipo comprador |
| GET | `/api/v1/me/transfer-offers` | El jugador: ofertas que esperan su decisión |
| POST | `/api/v1/contracts/{id}/lineup` | Administrador de un equipo del partido |

## Loop 4 — Verificación (salidas reales del 24/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 231 aprobadas, 4 omitidas (son las de PostgreSQL); 18 nuevas |
| `pytest` en PostgreSQL 16 + PostGIS | NO EJECUTADO: no hay PostgreSQL en este equipo |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 28 aprobadas (4 nuevas: monedas, ofertas, mercado, planilla) |
| Pruebas de componentes (`jest`) | 20 aprobadas (3 nuevas: modo manager y ofertas del jugador) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión propia (la revisión independiente queda pendiente)

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| ALTO | Si el comprador gastaba monedas entre la aceptación del DT y la del jugador, el traspaso habría dejado saldo negativo | El saldo se revisa de nuevo al completar, con el equipo bloqueado | `test_balance_is_checked_again_when_player_accepts` |
| MEDIO | Quitar a un jugador del mercado dejaba ofertas vivas por él | Se cancelan al quitarlo | Revisión de código + `test_offer_rules` |
| BAJO | El servicio de traspasos pasaba de 150 líneas | Separado `transfer_listing_service.py` | Toda la suite |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| ALTO | Traspasos cruzados y gastos simultáneos sin prueba en PostgreSQL | Agregar a `test_concurrency_pg.py` junto con reservas y firmas |
| MEDIO | Valores de premios y presupuesto inicial son supuestos | Ajustarlos con el dueño antes del piloto |
| MEDIO | [POR VERIFICAR] Si algún día se vendieran monedas, revisión legal (juegos de suerte y azar, consumo) | Mantener: no se venden |
| MEDIO | Sin migraciones: 4 tablas nuevas | Alembic antes del piloto |
| BAJO | La app no avisa cuando llega una oferta de traspaso (hay que abrir "Ofertas de traspaso") | Notificaciones push |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd backend; .\venv\Scripts\python.exe -m app.tools.health_check
cd mobile; npm run typecheck; npm test
```
