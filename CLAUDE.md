# Reglas del proyecto RIVAL

Metodología: prompt unificado FIIN adaptado a RIVAL (documento del Sprint 0: https://claude.ai/artifact/L8a8Uxfry9atkVTWMjWXg3).

## Forma de trabajo

- Scrum por Sprints con 5 loops rotulados: Research → Planning → Implementation → Verification & QA → Review & Retrospective. PO, SM y Developers intervienen en cada Sprint.
- Plan → Test → Implement → Review → Verify. Nada está "terminado" sin prueba ejecutada y salida conservada.
- Etiquetas de evidencia: [VERIFICADO EN ENTORNO] · [VERIFICADO EN FUENTE] · [INFERENCIA] · [SUPUESTO] · [SIMULACIÓN] · [POR VERIFICAR].
- Máximo una pregunta consolidada por respuesta, solo si cambia arquitectura, legalidad, seguridad o resultado.

## Reglas innegociables

- Máximo 150 líneas por archivo de código.
- Capas: backend `domain/ persistence/ services/ api/`; móvil `src/domain/ src/services/ src/controllers/ src/ui/`. Nunca HTTP ni SQL en una vista.
- TypeScript estricto: cero `any`, `import type` para tipos.
- Español en documentación y mensajes al usuario; inglés en identificadores, rutas y commits.
- Sin ubicación exacta de personas: solo cercanía por rangos, barrio y ciudad.
- Solo mayores de 18. Sin dinero dentro de la app: árbitros y canchas se pagan por fuera.
- Acceso universal a la navegación; las acciones sensibles se autorizan en el backend por rol dentro del equipo o la liga.
- Auditoría nominal con hash encadenado para equipos, solicitudes, contratos, resultados y traspasos.
- Ningún traspaso de jugador sin su aceptación. Las monedas RIVAL son virtuales y no se compran ni se venden.

## Comandos

```
cd backend
python -m pytest -v

cd mobile
npx tsc --noEmit
```
