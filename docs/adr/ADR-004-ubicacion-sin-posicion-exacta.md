# ADR-004 — Ubicación por cercanía, barrio o ciudad; nunca posición exacta

- **Fecha:** 23/11/2026
- **Estado:** Aceptada (decisión del dueño del producto)

## Contexto

La ubicación es dato personal (Ley 1581 de 2012). Google Play solo aprueba ubicación en segundo plano cuando es la función principal y recomienda la ubicación en primer plano (https://support.google.com/googleplay/android-developer/answer/9799150, consultado 23/11/2026).

## Decisión

- Se guarda el barrio y la ciudad elegidos por el usuario, no coordenadas de personas.
- El GPS es opcional, solo "mientras se usa la app", y sirve para sugerir el barrio; la posición se descarta.
- Las distancias se muestran por rangos (menos de 2 km, 2 a 5 km, más de 5 km).
- Las búsquedas tienen límite de peticiones para impedir triangular la ubicación de alguien.
- Los establecimientos sí muestran su dirección.

## Consecuencias

- Sprint 1: ciudad y barrio como texto validado. Sprint 2: catálogo de barrios con centro geográfico.
