# Sprint 20 — Carta del jugador y primera prueba en un iPhone

- **Fecha:** 25/11/2026
- **Meta (PO):** llevar a la app la carta del jugador aprobada en el lienzo de diseño (lámina metálica que se voltea) y probar RIVAL por primera vez en un teléfono real.
- **Estado:** Verificado en SQLite, en PostgreSQL 16 local, en pruebas de la app y **en el iPhone del dueño** ("se ve bien"). Pendiente: revisión independiente y la foto de perfil.

## Primera prueba en un dispositivo (Expo Go en iPhone)

| Flujo | Resultado en el iPhone |
| --- | --- |
| Abrir la app con Expo Go | Funcionó tras iniciar sesión en Expo en el computador y el teléfono (Expo Go en iOS lo exige) |
| Retar, recibir la oferta, aceptarla y firmar el contrato | Funcionó (el rival lo hizo `dev_tools/rival_bot.py`) |
| Reservar cancha y que la confirme el establecimiento | Funcionó |
| Chat del partido | Funcionó; la respuesta apareció sola |
| Teclado | **Tapaba los campos**: corregido en `Screen.tsx` (las 48 pantallas) y confirmado en el iPhone |
| Carta del jugador | Confirmada por el dueño: "se ve bien" |
| Check-in y resultado | No probados: dependen de la hora del partido (mañana) |

## Carta del jugador

- **Frente:** lámina metálica por nivel (bronce, plata, oro, élite) con un brillo que la recorre; no se anima si el teléfono pide reducir movimiento. Media, posición, escudo con iniciales, silueta (la foto queda para otro sprint), nombre y seis estadísticas reales: PJ, VIC, GOL, VAL, TRI, INS.
- **Reverso** (giro 3D al tocarla): récord, goles por partido, votos de compañeros, últimos 5 partidos, insignias y lo que falta para el siguiente nivel.
- **Estilo propio de RIVAL:** inspirado en los juegos de fútbol, sin copiar marcos, logos, tipografías ni las siglas de atributos de ningún juego; sin fotos de futbolistas reales ni escudos de clubes.
- **Media (0 a 99)** [SUPUESTO, ajustable]: base 40; hasta 30 por la valoración de compañeros (con menos de 3 votos cuenta 5,5, neutral); hasta 15 por experiencia (tope 50 partidos); hasta 10 por porcentaje de victorias; hasta 4 por goles por partido. Redondeo de ,5 hacia arriba. Un jugador nuevo empieza en 57.
- **Nivel** por partidos confirmados: Bronce 0 a 9, Plata 10 a 19, Oro 20 a 29, Élite 30 o más.
- Nada de la carta se compra: sube jugando. Las monedas RIVAL siguen siendo virtuales.
- **Diferencia con el lienzo:** bordes redondeados en lugar de esquinas recortadas; recortarlas exige `react-native-svg`.
- **Dependencia nueva:** `expo-linear-gradient` (oficial de Expo), aprobada por el dueño.

## Herramientas de prueba (solo base local)

- `dev_tools/seed_test_rival.py`: usuario rival y su equipo.
- `dev_tools/seed_test_venue.py`: establecimiento, cancha y franja; la ubicación la fija su dueño desde el teléfono.
- `dev_tools/rival_bot.py`: rival automático que oferta, firma, contesta el chat, repite el marcador y confirma reservas.
- Credenciales de prueba en el encabezado de cada script; nunca usarlos contra datos reales.

## API

`GET /api/v1/players/{id}/card` ahora incluye `card`: `media`, `tier`, `next_tier`, `matches_to_next`, `hat_tricks`, `recent` y `badges`.

## Loop 4 — Verificación (salidas reales del 25/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 328 aprobadas, 10 omitidas (las de PostgreSQL); 4 nuevas |
| `pytest` completo en PostgreSQL 16 local | 338 aprobadas, 0 omitidas |
| `alembic check` en PostgreSQL (sin migración nueva) | Sin diferencias |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 54 aprobadas (3 nuevas) |
| Pruebas de componentes (`jest`) | 48 aprobadas (1 nueva) |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| iPhone con Expo Go | Flujos de la tabla de arriba; carta y teclado confirmados por el dueño |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| MEDIO | `round()` de Python redondea los ,5 al par: una media de 84,5 daba 84 | Redondeo explícito hacia arriba; pruebas con casos de ,5 |
| BAJO | "Faltan 1 partido" | "Falta 1 partido" |
| BAJO | Una prueba esperaba 84 por un error de cuenta (85,5) | Corregida con el cálculo escrito al lado |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | Sin foto de perfil en la carta | Sprint propio: almacenamiento, borrar el GPS de la imagen, moderación y decidir quién la ve |
| MEDIO | La fórmula de la media es un supuesto | Ajustarla con el piloto |
| BAJO | El resto de la app aún no usa la identidad "Cancha al sol" ni la barra de pestañas | Siguiente parte del rediseño, por pantallas |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
cd mobile; npx tsc --noEmit; npm test
cd backend; .\venv\Scripts\python.exe dev_tools\rival_bot.py
```
