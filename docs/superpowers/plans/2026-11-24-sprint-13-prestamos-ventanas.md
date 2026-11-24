# Sprint 13 — Modo manager 2: préstamos por un partido y ventanas de traspasos — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [x]`).

**Meta:** pedir prestado "el que falta" a otro equipo para un partido, con la aceptación de su DT y del jugador; y que cada liga tenga ventanas de traspasos para que los equipos no cambien de plantilla en plena temporada (Sprint 0, sección 4.2.2).

## Reglas

- **Préstamo:** el administrador de un equipo con un partido (contrato) no cancelado y antes de la hora pide prestado a un jugador con rol PLAYER de otro equipo del mismo deporte. No a un jugador del equipo rival de ese partido ni de su propio equipo. Primero acepta el administrador del equipo dueño; después el jugador (nadie acepta por él). Un préstamo activo o pendiente por jugador y partido.
- Con el préstamo activo, el jugador puede ser convocado y aparecer en la planilla de ese partido, solo de ese partido. No cambia de equipo ni se mueven monedas [SUPUESTO: préstamo gratuito].
- Cualquiera de los dos administradores o el jugador puede cancelar el préstamo antes de la hora.
- **Ventana de traspasos:** el organizador o un coorganizador fija en su liga una ventana (inicio y fin). [SUPUESTO] Sin ventana configurada, los traspasos están abiertos. Si cualquiera de los dos equipos está aprobado en una liga cuya ventana está cerrada en ese momento, no se puede ofertar ni completar el traspaso (`TRANSFER_WINDOW_CLOSED`).
- Auditoría de todo; los eventos del préstamo aparecen en la actividad del partido.

## Tareas

- [x] Dominio `loan_rules.py` / reglas de ventana; persistencia `league.transfer_window_*` y tabla `player_loan`; migración `0004`.
- [x] Servicios `loan_service.py`; préstamos en convocatoria y planilla; ventana en `transfer_service` y `league_service`.
- [x] API y pruebas; PostgreSQL local.
- [x] App: pedir préstamo desde el contrato, decidir (DT dueño y jugador), ventana en la liga.
- [x] CI con Node 22.15 fijo, verificación y `docs/sprint-13.md`.
