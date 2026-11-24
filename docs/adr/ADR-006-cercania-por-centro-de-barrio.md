# ADR-006 — Cercanía calculada entre centros de barrio, sobre el catálogo

- **Fecha:** 23/11/2026
- **Estado:** Aceptada (precisa ADR-003 y ADR-004)

## Contexto

RIVAL nunca guarda la posición de una persona (ADR-004). Lo único con coordenadas es el catálogo de barrios: un punto central por barrio. Barranquilla, la ciudad piloto, tiene 177 barrios según el Anuario Estadístico 2020 de la Alcaldía (https://barranquilla.gov.co/documento/anuario-estadistico-2020-cap-2-territorio-y-medio-ambiente, consultado 23/11/2026).

## Opciones

| Opción | A favor | En contra |
| --- | --- | --- |
| `ST_DWithin` de PostGIS sobre la tabla de equipos | Índice GiST, escala a millones de puntos | Exige guardar un punto por equipo; solo corre en PostgreSQL con PostGIS |
| Distancia entre centros de barrio sobre el catálogo (haversine) y luego filtrar equipos por `neighborhood_id` | Funciona igual en SQLite y PostgreSQL; el catálogo tiene cientos de filas por ciudad; ningún equipo ni persona tiene coordenadas propias | Si el catálogo creciera a decenas de miles de barrios por consulta habría que moverlo a PostGIS |

## Decisión

1. La distancia se calcula entre el centro del barrio del equipo que busca y el centro de cada barrio del catálogo de la misma ciudad (fórmula de haversine, radio terrestre medio 6.371 km).
2. Los barrios dentro del radio se convierten en una lista de `neighborhood_id` y la consulta de equipos filtra por esa lista.
3. A las personas solo se les muestra el **rango**: "menos de 2 km", "2 a 5 km" o "más de 5 km".
4. Si un barrio no tiene coordenadas en el catálogo, "Cerca de mí" no lo incluye y la búsqueda sigue disponible por barrio y ciudad.
5. El catálogo se importa desde un CSV (`nombre;ciudad;lat;lon;fuente`). La fuente prevista para Barranquilla es el "Mapa de Barrios de Barranquilla Según el POT" en datos.gov.co [POR VERIFICAR: descargar y convertir a centroides]. Las pruebas usan barrios sintéticos rotulados [SIMULACIÓN].
6. PostGIS sigue siendo la base de producción (ADR-003) y se usará si el volumen lo exige.

## Consecuencias

- Las coordenadas del catálogo usan `Numeric(9,6)`; los cálculos de distancia usan `float` porque no son dinero.
- Las búsquedas por radio tienen límite de peticiones para impedir triangular dónde juega un equipo.
