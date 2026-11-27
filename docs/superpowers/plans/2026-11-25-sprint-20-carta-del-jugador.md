# Sprint 20 — Carta del jugador (plan)

**Meta:** llevar a la app la carta aprobada en el lienzo de diseño: lámina metálica, media, nivel y reverso con la ficha completa, todo con datos reales.

## Fórmula de la media (0 a 99) [SUPUESTO, ajustable]

Solo partidos con resultado confirmado y con el jugador en la planilla.

| Parte | Puntos | Cómo |
| --- | --- | --- |
| Base | 40 | Todos empiezan aquí |
| Valoración de compañeros | hasta 30 | promedio (1 a 10) × 3; con menos de 3 votos cuenta 5,5 (neutral) |
| Experiencia | hasta 15 | partidos jugados, tope en 50 |
| Efectividad | hasta 10 | porcentaje de victorias |
| Gol | hasta 4 | goles por partido, tope en 1 |

Nadie llega a 99 sin jugar mucho, ganar y que sus compañeros lo valoren bien. La media nunca se compra.

## Nivel de la carta (por partidos confirmados)

Bronce 0 a 9 · Plata 10 a 19 · Oro 20 a 29 · Élite 30 o más. El reverso muestra cuántos faltan para el siguiente.

## Tareas

- [x] `domain/card_rules.py` (media, nivel, siguiente nivel) y pruebas.
- [x] La ficha del jugador agrega media, nivel, victorias, tripletes, últimos 5 resultados e insignias ganadas.
- [x] App: `expo-linear-gradient` (aprobado), componente de carta metálica con brillo y volteo; reemplaza la ficha actual.
- [x] Pruebas, tsc, prettier, 150 líneas; prueba en el iPhone.
- [x] Verificar en PostgreSQL; `docs/sprint-20.md`.

Fuera de este sprint: la foto de perfil (necesita almacenamiento, borrar el GPS de la imagen y moderación).
