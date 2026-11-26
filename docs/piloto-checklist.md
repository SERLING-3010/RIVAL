# Checklist para el piloto

Lo que falta para pasar de «probar en mi iPhone» a un piloto con equipos reales. Cada punto dice quién lo hace: el dueño (D), Claude (C) o ambos (D+C).

## Legal y datos personales (Ley 1581 de 2012)

- [ ] (D) Revisión de `docs/legal/terminos.md` y `docs/legal/politica-privacidad.md` por alguien con formación jurídica: un consultorio jurídico universitario, la Cámara de Comercio o un abogado por horas.
- [ ] (D) Llenar los [POR DEFINIR] de la política: nombre, cédula o NIT, dirección, correo, teléfono, quién atiende las solicitudes, el proveedor del servidor y la fecha de inicio.
- [ ] (D) Inscribir la base de datos en el RNBD de la SIC, si aplica según el tamaño de la empresa [POR VERIFICAR con el abogado].
- [x] (C) Aceptación versionada de términos y privacidad, con la mayoría de edad declarada (Sprint 27).
- [x] (C) Descargar mis datos y eliminar la cuenta anonimizándola (Sprint 27).
- [x] (C) Avisos push sin datos personales (Sprint 24).

## Servidor y base de datos

- [ ] (D) Elegir dónde se aloja: un servidor en la nube con PostgreSQL administrado y copias de seguridad automáticas.
- [ ] (C) Preparar el despliegue: Dockerfile del backend, variables de entorno (`RIVAL_DATABASE_URL`, el catálogo y los tiempos de sesión), `alembic upgrade head` al desplegar y HTTPS obligatorio.
- [ ] (C) Tareas programadas: `python -m app.tools.push_worker` (cada minuto) y `python -m app.tools.purge_sessions` (cada día).
- [ ] (D+C) Probar la restauración de una copia de seguridad antes de abrir el piloto.
- [ ] (C) Monitoreo mínimo: `python -m app.tools.health_check` y alertas de errores 5xx.

## App

- [ ] (D+C) Versión de desarrollo o TestFlight con EAS si Expo Go no entrega avisos remotos.
- [ ] (D) Cuenta de Apple Developer (y de Google Play si habrá Android) para distribuir la app.
- [ ] (C) Apuntar `EXPO_PUBLIC_API_URL` al servidor del piloto, que debe usar HTTPS.
- [ ] (D) Medir en un teléfono real el rendimiento de la plantilla con muchas cartas animadas.

## Operación

- [ ] (D) Nombrar a los moderadores del piloto (`python -m app.tools.grant_moderator`).
- [ ] (D) Cargar los barrios reales de la ciudad del piloto (`python -m app.tools.import_neighborhoods`).
- [ ] (D) Definir un canal de soporte para que la gente pida ayuda o cierre una cancha.
