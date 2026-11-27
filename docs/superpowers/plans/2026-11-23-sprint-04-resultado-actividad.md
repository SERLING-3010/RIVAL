# Sprint 4 — Resultado, central de actividad y centro de salud — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** después de jugar, los dos administradores reportan el marcador; el resultado vale cuando ambos coinciden y, si no, queda en disputa. Cada equipo y cada partido muestran quién hizo cada cambio, con antes y después. Un chequeo determinista detecta los estados que nunca deberían existir.

**Spec:** documento del Sprint 0, secciones 4.4.1, 4.7, 7.5, 7.6 y 9.3 (RIV-013, RIV-014). Pendiente del Sprint 1: "Centro de salud (Sprint 4)".

## Alcance [SUPUESTO del equipo, reversible]

- RIV-013 sin árbitro: aún no hay árbitros en la app (RIV-010). La confirmación del árbitro llega con ese Sprint.
- Sin W.O. ni incidencias (tarjetas): solo marcador.
- Centro de salud como herramienta de línea de comandos; no hay rol de administrador del sistema para verlo en la app.

## Reglas

- Solo se reporta un partido con versión firmada, no cancelado y cuya hora de inicio ya pasó.
- Marcador entero de 0 a 999 por equipo.
- Un reporte por equipo; se puede corregir mientras el resultado no esté confirmado.
- Dos reportes iguales: CONFIRMED (inmutable). Distintos: DISPUTED, hasta que uno corrija y coincidan. Uno solo: PENDING.
- Solo administradores reportan; los miembros de ambos equipos ven el resultado y los reportes.
- Actividad: miembros del equipo ven los eventos del equipo, sus solicitudes, búsquedas, ofertas y contratos; miembros de los dos equipos ven los del partido. Nunca contraseñas, tokens ni correos.
- Centro de salud: cadena de auditoría rota (S0), contrato firmado sin dos firmas en la versión firmada (S0), equipo sin administrador (S1), búsqueda MATCHED sin contrato (S1), partido firmado sin resultado confirmado 48 h después de la hora (S3).

## Tareas

- [x] Dominio `result_rules.py` con pruebas.
- [x] Persistencia `models_results.py`.
- [x] Servicios `result_service.py`, `activity_service.py`, `health_service.py`; herramienta `tools/health_check.py`.
- [x] API: resultado en el contrato, `/contracts/{id}/activity`, `/teams/{id}/activity`.
- [x] App: reportar marcador en el contrato, marcador en "Partidos pactados", pantalla de actividad.
- [x] Verificación y `docs/sprint-04.md`.
- [ ] Revisión independiente y prueba en PostgreSQL (pendientes).
