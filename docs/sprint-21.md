# Sprint 21 — El capitán maneja el día del partido

- **Fecha:** 25/11/2026
- **Meta (PO):** que el capitán ayude con el día del partido cuando hay DT, sin perder un único responsable para lo que compromete al equipo frente a otros. Y dejar diseñada la pantalla del equipo en modo juego.
- **Estado:** Verificado en SQLite, en PostgreSQL 16 local, y en pruebas de la app. La pantalla del equipo en modo juego está solo en el lienzo de diseño (página "Modo manager"), todavía no en la app.

## Decisión del dueño (25/11/2026)

| Acción | DT | Capitán | Jugadores |
| --- | --- | --- | --- |
| Ver plantilla, alineación, convocatoria, contratos y chat | ✓ | ✓ | ✓ |
| Responder convocatoria, check-in, valorar compañeros | ✓ | ✓ | ✓ |
| Enviar convocatoria, armar alineación y planilla | ✓ | ✓ | — |
| Reportar el resultado | ✓ | ✓ | — |
| Retar, aceptar ofertas, firmar, reservar cancha | ✓ | Solo si no hay DT | — |
| Mercado, traspasos, préstamos, bloqueos, nombrar capitán | ✓ | Solo si no hay DT | — |

## Decisiones

- **Regla en el dominio:** `team_rules.is_matchday_staff` = el administrador (DT, o capitán si no hay DT) o el capitán. No se guarda nada nuevo: se calcula de los roles, como el administrador.
- **`matchday_staff.staff_side`** reemplaza a `admin_side` solo en convocatoria, alineación táctica, planilla y resultado. Firmas, retos, cancha, mercado, traspasos y préstamos siguen con `admin_side`, para que la auditoría nombre siempre a un único responsable de lo que compromete al equipo.
- Si el DT y el capitán reportan el resultado, vale el último reporte de su equipo (el resultado es uno por equipo).
- **La app** recibe `is_staff` en el contrato: el capitán ve "Reportar marcador", "Registrar planilla", el envío de convocatoria y la edición de la alineación.

## Diseño (lienzo, página "Modo manager")

- **Equipo · Titulares:** panel con media del equipo, formación, récord, nivel e insignias; cartas sobre la cancha con su posición y la marca "C" del capitán; suplentes abajo.
- **Equipo · Jugadores:** todas las cartas en cuadrícula, ordenables por media, posición o partidos, con las marcas DT y C.
- **Equipo · Comparar:** hexágono con seis datos reales (partidos, goles, victorias, valoración, puntualidad, insignias) y barras enfrentadas.
- En vertical, para usar con una mano; estilo propio de RIVAL, sin activos de EA ni de clubes; medias de 0 a 99.

## Loop 4 — Verificación (salidas reales del 25/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 330 aprobadas, 10 omitidas (las de PostgreSQL); 2 nuevas |
| `pytest` completo en PostgreSQL 16 local | 340 aprobadas, 0 omitidas |
| `alembic check` en PostgreSQL (sin migración nueva) | Sin diferencias |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`node --test`) | 55 aprobadas (1 nueva) |
| Pruebas de componentes (`jest`) | 48 aprobadas |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| En el iPhone | NO EJECUTADO todavía (el backend del teléfono ya corre con este cambio) |

## Revisión propia

| Impacto | Hallazgo | Corrección |
| --- | --- | --- |
| BAJO | `contract_queries.py` quedaba cerca del límite si sumaba la regla | La regla quedó en el dominio y el lado del contrato en `matchday_staff.py` |
| BAJO | Una prueba de la app dejó su archivo en 152 líneas | Prueba compactada; el archivo queda en 150 |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | La pantalla del equipo en modo juego no está en la app | Siguiente sprint: llevarla del lienzo a la app |
| BAJO | El DT no puede quitarle permisos al capitán | Si el piloto lo pide, un ajuste por equipo |
