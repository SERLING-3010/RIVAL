# Sprint 23 — Cartas básicas por media y especiales por hazañas

- **Fecha:** 25/11/2026
- **Meta (PO):** que la carta dé ganas de jugar mejor. Las cartas básicas salen de la media. Las especiales, de Rubí a Élite, son difíciles de conseguir: piden media y hazañas (goles, tripletes, póker, chilena, olímpico…). Cada jugador tiene además un valor de mercado en monedas virtuales.
- **Estado:** Verificado en SQLite, en PostgreSQL 16 local y en las pruebas de la app. Falta probarlo en el iPhone. Este sprint reemplaza la versión de 18 niveles por partidos de este mismo sprint, que nunca se confirmó en git.

## Decisiones del dueño (25/11/2026)

1. **Cartas básicas por media:** Bronce hasta 64, Plata de 65 a 74, Oro común de 75 a 79 y Oro brillante (única) desde 80.
2. **Cartas especiales por media + hazañas**, de Rubí en adelante.
3. **Élite = Aurora + Neón.** Corona, Prisma y Galaxia son especiales de la clase Suprema.
4. **Goles con tipo:** el DT o el capitán los marca en la planilla, y el DT o el capitán rival los confirma o los rechaza.

## Cartas especiales [SUPUESTO: requisitos ajustables con el piloto]

| Carta | Media | Hazaña |
| --- | --- | --- |
| Rubí | 75 | 10 goles |
| Esmeralda | 75 | 3 tripletes |
| Diamante | 78 | 1 póker (4 goles en un partido) |
| Zafiro Padparadscha | 78 | 25 goles |
| Alejandrita | 80 | Gol de chilena |
| Diamante Fantasía | 80 | Gol olímpico |
| Grandidierita | 82 | 3 goles de tiro libre |
| Serendibita | 82 | Manita (5 goles en un partido) |
| Painita | 84 | 50 goles |
| Taaffeíta | 85 | 10 tripletes |
| Diamante Rojo | 86 | Chilena + olímpico + 100 goles |
| Corona | 87 | Campeón de copa |
| Prisma | 88 | 5 tipos de gol distintos (los goles sin tipo cuentan como uno) |
| Galaxia | 90 | 150 goles |
| Élite | 92 | Top 3 de media en su ciudad |

## Decisiones técnicas

- **Dominio:**
  - `card_rules.tier(media)` calcula la carta básica.
  - `special_cards` tiene la tabla de las 15 especiales con sus hazañas, `progress`, `best` y `validate_kinds`.
  - Las hazañas salen solo de partidos con resultado confirmado.
- **Goles con tipo:**
  - La tabla `goal_claim` (migración `0009`) guarda cada gol con tipo: cabeza, penal, tiro libre, chilena u olímpico.
  - La planilla los crea como pendientes. Corregir la planilla los vuelve a dejar pendientes.
  - El rival los confirma o los rechaza con `POST /goal-claims/{id}/decision`. No puede hacerlo el mismo equipo (`RIVAL_ONLY`), y después de 72 horas ya no se puede (`GOAL_CLAIM_EXPIRED`).
  - Un gol rechazado o vencido sigue contando como gol normal.
  - Cada decisión queda en la auditoría encadenada: `GOAL_KIND_CONFIRMED` o `GOAL_KIND_REJECTED`, con quién lo marcó y quién lo aprobó.
- **Orden de bloqueo:** la decisión bloquea primero el contrato y después el gol, igual que la planilla, para que no haya interbloqueos.
- **Cartas ganadas:**
  - La tabla `special_card` las guarda con una restricción única por jugador y carta.
  - Se otorgan la primera vez que se ve la carta cumpliendo los requisitos [SUPUESTO: no hace falta un proceso aparte]. Si dos lecturas compiten, un savepoint absorbe el choque.
  - No se pierden aunque la media baje.
- **Qué carta se dibuja:** la especial más difícil que tenga el jugador, o si no tiene ninguna, su básica (`display_tier`). Vale para la ficha y para la plantilla.
- **Valor de mercado [SUPUESTO]:** media × 5, más 25 por cada carta básica por encima de Bronce, más 40 por cada especial, más la forma (10 por victoria y 4 por empate en los últimos 5 partidos). Se redondea a decenas. Son monedas virtuales: no se compran ni se venden.
- **Pendientes:** el DT o capitán rival ve «Confirmar goles especiales», marcado como urgente y con vencimiento a las 72 horas.
- **App:**
  - La ficha muestra la carta básica con su barra de media, las 3 especiales más cercanas con cada hazaña (por ejemplo «3 tripletes: 1 / 3»), el valor de mercado y el álbum de 15.
  - En la planilla, cada jugador con goles tiene botones para marcar el tipo de cada gol.
  - El contrato muestra «Goles especiales» con «Confirmar» y «No fue así» para el rival.
- **Diseños:** cada carta tiene el suyo (`cardTiers.ts`, `TierEffects`, `TierEmblem`). Son propios de RIVAL, sin marcos, logos ni tipografías de juegos comerciales.

## Barra del equipo y cierre de temporada (pedido del dueño, 25/11/2026)

- **La barra del equipo es la de siempre** (decisión del dueño, 25/11/2026). Solo cambia el cuadro de la media, que toma el diseño de la carta del equipo: bronce, plata, oro, rubí…
  - **Diseño del cuadro:** el DT lo mantiene presionado y elige entre «Automático: la mejor», su básica o cualquier especial que el equipo ya ganó (`POST /teams/{id}/card-choice`). No puede elegir una especial que no haya ganado (`DESIGN_NOT_OWNED`).
  - **Escudo:** reemplaza la «C». El predeterminado es el cuadro verde con las iniciales. El DT lo mantiene presionado y lo arma con piezas de RIVAL: forma (escudo, círculo, rombo o bandera), dos colores de la paleta y un símbolo (iniciales, estrella, rayo, corona o balón), con `POST /teams/{id}/crest`. No se suben imágenes [DECISIÓN TÉCNICA]: así no hay fotos que guardar, a las que quitar datos ocultos como la ubicación ni que moderar, igual que con la foto de perfil pendiente.
  - **Permisos y auditoría:** solo el administrador del equipo los cambia (`ADMIN_ONLY`), y cada cambio queda en la auditoría (`TEAM_CREST_CHANGED`, `TEAM_DESIGN_CHOSEN`). Los dos datos se guardan en el equipo (migración `0011`).
  - **Álbum:** al tocar la barra se abre el álbum del equipo, con las 3 especiales más cercanas y las 15 casillas.
- **La carta básica del equipo** sale de la media de sus titulares, con los mismos rangos que la del jugador.
- **Especiales del equipo** (`team_special_cards`) [SUPUESTO: requisitos ajustables]. Usan los mismos códigos y diseños que las del jugador, y se ganan una vez y para siempre (tabla `team_special_card`):

| Carta | Media | Hazaña |
| --- | --- | --- |
| Rubí | 75 | 10 victorias |
| Esmeralda | 75 | 50 goles |
| Diamante | 78 | 5 vallas invictas |
| Zafiro Padparadscha | 78 | 25 victorias |
| Alejandrita | 80 | Racha de 5 victorias |
| Diamante Fantasía | 80 | Una goleada (por 5 o más) |
| Grandidierita | 82 | 10 vallas invictas |
| Serendibita | 82 | 10 partidos sin perder |
| Painita | 84 | 200 goles |
| Taaffeíta | 85 | 50 victorias |
| Diamante Rojo | 86 | 100 victorias y 3 goleadas |
| Corona | 87 | Campeón de copa |
| Prisma | 88 | Campeón de liga |
| Galaxia | 90 | Doblete: liga y copa de la misma liga |
| Élite | 92 | Top 3 de nivel en su ciudad |

- **Cierre de temporada** (`season_service.close`, `POST /leagues/{id}/close-season`):
  - Solo lo hace el organizador.
  - Exige que todos los partidos del calendario tengan resultado confirmado o estén cancelados, y que se haya jugado al menos uno.
  - Gana el primero de la tabla.
  - La liga guarda `champion_team_id` y `closed_at` (migración `0010`); su estado sigue siendo activo, así que la liga sigue visible.
  - No se puede reabrir y queda en la auditoría como `LEAGUE_SEASON_CLOSED`.
  - En la app, el organizador ve «Cerrar temporada» con una confirmación. Después todos ven «🏆 Campeón».
- **Reverso de las cartas:** usa la misma lámina y los mismos efectos que el frente (`TierFoil`), en la ficha, en Titulares y en Jugadores.
- **Detalles corregidos en el iPhone:**
  - La media ya no se parte en dos líneas.
  - La C o DT va pequeña dentro de la carta, en la esquina superior derecha.
  - «GOLES/PARTIDO» ahora dice «G/P».

## Loop 4 — Verificación (salidas reales del 25/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 357 aprobadas, 10 omitidas (las de PostgreSQL) |
| `pytest` completo en PostgreSQL 16 local | 367 aprobadas, 0 omitidas (versión final). Una corrida anterior con el código a medias tuvo 1 falla que no se repitió: intermitente [POR VERIFICAR], igual que la del CI de c92707e |
| Migraciones `0009`, `0010` y `0011` en PostgreSQL vacío | `upgrade head`, `alembic check` sin diferencias, bajar y volver a subir cada una, todo bien |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 60 aprobadas |
| Pruebas de componentes (`jest`) | 77 aprobadas (22 suites) |
| Líneas por archivo / `any` | Ninguno pasa de 150; sin `any` |
| En el iPhone | Cartas, ficha y plantilla revisadas por el dueño; los arreglos que pidió quedaron aplicados. La barra del equipo y el cierre de temporada todavía no se han revisado en el teléfono |

## Pendiente y riesgos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | La pantalla «¡Nueva carta!» no está en la app | Ya existe `earned_at`: mostrarla cuando haya una especial ganada después de la última visita |
| MEDIO | Élite calcula la media de todos los jugadores de la ciudad (solo si el jugador ya tiene 92) | Si la ciudad crece, guardar un ranking calculado |
| MEDIO | La carta especial se otorga al leer la ficha | Si se necesita que aparezca sin que nadie abra la ficha, otorgarla al confirmar el resultado o el gol |
| BAJO | No se ha medido el rendimiento de muchas cartas animadas en un teléfono real | Probarlo en el iPhone |
