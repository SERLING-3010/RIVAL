# ADR-003 — PostgreSQL + PostGIS como fuente de verdad

- **Fecha:** 23/11/2026
- **Estado:** Aceptada; SQLite solo en desarrollo del Sprint 1

## Contexto

La búsqueda por cercanía necesita consultas por radio con índice. PostGIS ofrece `geography(Point,4326)`, índices GiST y `ST_DWithin`, que usa el índice y es más rápida que `ST_Distance` (https://postgis.net/documentation/tips/st-dwithin, consultado 23/11/2026).

## Decisión

- Producción: PostgreSQL + PostGIS; Row Level Security como segunda barrera.
- Las distancias se calculan desde el centro del barrio (catálogo `neighborhood`), nunca desde la posición de una persona.
- Sprint 1 (sin búsqueda geográfica): SQLite para que el proyecto corra en Windows sin instalar nada más. La migración a PostgreSQL entra en el Sprint 2 con migraciones versionadas.
- Redis solo para caché, límites de peticiones y colas.

## Consecuencias

- El código de persistencia usa SQLAlchemy 2 sin funciones exclusivas de SQLite.
