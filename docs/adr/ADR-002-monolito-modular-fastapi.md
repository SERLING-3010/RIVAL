# ADR-002 — Monolito modular con FastAPI

- **Fecha:** 23/11/2026
- **Estado:** Aceptada

## Contexto

Equipo pequeño, producto nuevo, reglas de dominio con muchas relaciones (equipos, ligas, contratos, árbitros, canchas). No hay evidencia de que haga falta escalar por separado ningún módulo.

## Opciones

- Monolito modular (un solo despliegue, módulos con límites claros).
- Microservicios (despliegues independientes, más infraestructura y fallos de red entre módulos).

## Decisión

Monolito modular FastAPI con capas `domain` (reglas puras, sin dependencias), `persistence` (SQLAlchemy), `services` (casos de uso, auditoría) y `api` (rutas y esquemas). Módulos previstos: identity, teams, leagues, matchmaking, match_contract, referees, venues, audit, health.

## Consecuencias

- Las reglas se prueban sin base de datos ni HTTP.
- Si un módulo necesita separarse, sus límites ya existen.
