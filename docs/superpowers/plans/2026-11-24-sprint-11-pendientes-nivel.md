# Sprint 11 — Pendientes y rivales de nivel parecido — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** que nadie se entere tarde de lo que le toca hacer: una bandeja "Pendientes" en el inicio reúne todo lo que espera la acción del usuario. Y al buscar rival, el DT puede ordenar por nivel parecido.

**Spec:** riesgos abiertos de los Sprints 4, 7 y 10 ("la app no avisa"); documento del Sprint 0, sección 5.3 (emparejamiento por nivel).

## Reglas

- **Pendientes** se calculan en cada consulta (sin tablas nuevas ni copias de datos), solo de lo que el usuario puede hacer y aún está a tiempo:
  - Firmar: administrador de un equipo con contrato en negociación cuya versión vigente su equipo no ha firmado, antes de la hora.
  - Reportar marcador: administrador de un equipo con partido firmado, ya empezado, sin resultado confirmado y sin reporte de su equipo, o en disputa.
  - Convocatoria: convocado sin responder a un partido futuro no cancelado.
  - Traspaso: oferta que espera al jugador; oferta que espera al administrador del equipo dueño.
  - Solicitudes de unión: administrador de un equipo con solicitudes pendientes.
  - Árbitro: asignación por aceptar; o asignación aceptada con partido ya empezado y sin resultado confirmado.
  - Reserva: dueño de establecimiento con reservas por confirmar de partidos futuros.
  - Liga: personal con solicitudes de equipos o árbitros por decidir.
  - Valorar compañeros: partido con resultado confirmado en los últimos 7 días, con compañeros por valorar.
- Cada pendiente trae el tipo, un texto en español y el id de lo que hay que abrir. Orden: lo más urgente primero (por hora del partido).
- **Nivel parecido:** la búsqueda de rivales acepta `order=level`: primero los equipos con nivel más cercano al propio; los que aún no tienen nivel, al final. Si mi equipo no tiene nivel, se usa 1500.

## Tareas

- [x] Servicio `pending_service.py` (+ `pending_sources.py` si pasa de 150 líneas) con pruebas.
- [x] Orden por nivel en `rival_service.py` con prueba.
- [x] API `GET /me/pending` y `order=level` en `/teams/{id}/rivals`.
- [x] App: tarjeta "Pendientes (N)" en el inicio, pantalla de pendientes que lleva a cada lugar, orden "Nivel parecido".
- [x] Verificación y `docs/sprint-11.md`.
- [ ] Revisión independiente (pendiente).
