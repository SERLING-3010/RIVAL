# ADR-005 — Rating de equipos con Glicko-2 (P1)

- **Fecha:** 23/11/2026
- **Estado:** Propuesta para P1

## Contexto

El emparejamiento debe sugerir rivales de nivel parecido. Un equipo nuevo no tiene historial.

## Decisión

Rating Glicko-2 por equipo y modalidad: además del nivel mide la incertidumbre (RD) y la volatilidad, de modo que un equipo nuevo tiene RD alta. Solo cuentan partidos con resultado confirmado por ambos administradores o por el árbitro.

## Consecuencias

- Hasta P1 el emparejamiento usa reglas deterministas (deporte, modalidad, alcance, franja horaria).
