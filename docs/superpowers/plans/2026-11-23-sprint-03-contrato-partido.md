# Sprint 3 — Contrato del partido con firmas — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** cuando un DT acepta una oferta nace el contrato del partido. Los dos administradores pactan las condiciones, cada cambio es una versión nueva y el contrato queda firmado solo cuando ambos firman la misma versión. Un cambio después de firmar exige la aceptación del rival; mientras tanto vale la versión firmada.

**Arquitectura:** mismas capas. Tablas nuevas `match_contract`, `match_contract_version` (inmutable: solo se insertan filas) y `match_contract_signature` (una por equipo y versión, índice único). El contrato guarda punteros a la versión vigente en negociación y a la última firmada.

**Spec:** documento del Sprint 0, secciones 4.4, 4.4.1, 6 y 9.3 (RIV-009).

## Restricciones globales

- Las de los Sprints 1 y 2.
- Condiciones validadas en dominio: hora de inicio futura y máximo 60 días adelante, duración 20–240 min, cambios 0–30 o ilimitados, colores de uniforme distintos, reparto de costos de cancha y árbitro (mitad, local, visitante), aviso de cancelación 0–72 h; si es sin árbitro, nota opcional de quién cobra las faltas dudosas.
- Sin dinero en la app: el reparto de costos es solo un acuerdo escrito; no hay montos.
- Proponer una versión equivale a firmarla por el equipo que propone. El rival firma esa versión o propone otra.
- Firmar exige indicar el número de versión: si cambió entretanto, 409 `CONTRACT_VERSION_CHANGED`.
- Toda mutación bloquea la fila del contrato (FOR UPDATE).
- Rechazar un cambio después de firmar devuelve el contrato a la versión firmada. Antes de la primera firma no hay "rechazo": se contrapropone o se cancela.
- Cancelar exige motivo (5–200 caracteres) y lo puede hacer cualquiera de los dos administradores mientras el partido no haya empezado.
- Solo miembros de los dos equipos ven el contrato; para cualquier otro no existe (404).
- Auditoría: CONTRACT_CREATED, CONTRACT_VERSION_PROPOSED, CONTRACT_SIGNED, CONTRACT_AMENDMENT_REJECTED, CONTRACT_CANCELLED, con antes y después.

## Estados

`NEGOTIATING` → (ambos firman la versión vigente) → `SIGNED` → (alguien propone cambio) → `NEGOTIATING` con versión firmada anterior conservada → (el rival firma: `SIGNED` con la nueva) o (el rival rechaza / el proponente retira: `SIGNED` con la anterior). `CANCELLED` desde `NEGOTIATING` o `SIGNED`. "Listo para jugar", "Jugado" y resultado llegan en Sprints posteriores (RIV-012, RIV-013).

## Review Focus

1. Ningún contrato pasa a SIGNED sin dos firmas sobre la misma versión.
2. Una versión firmada nunca cambia: un cambio crea versión nueva y la firmada sigue visible.
3. Firmar una versión que el rival acaba de reemplazar responde 409.
4. Un tercero (o un jugador que no es administrador) no puede firmar ni proponer.
5. Aceptar la oferta crea exactamente un contrato (índice único por búsqueda).

## Tareas

- [x] Dominio: `contract_rules.py` (condiciones, estados, validación) con pruebas.
- [x] Persistencia: `models_contracts.py`.
- [x] Servicios: `contract_service.py` (crear, proponer, firmar, rechazar, cancelar), `contract_views.py`; crear contrato al aceptar oferta.
- [x] API: `routes_contracts.py`, `schemas_contracts.py`.
- [x] App: lista de contratos, pantalla de contrato (condiciones, firmas, firmar, proponer cambio, rechazar, cancelar).
- [x] App: pruebas de componentes con jest-expo (deuda de los Sprints 1 y 2).
- [x] Verificación y `docs/sprint-03.md`.
- [ ] Revisión independiente y prueba en PostgreSQL (pendientes).
