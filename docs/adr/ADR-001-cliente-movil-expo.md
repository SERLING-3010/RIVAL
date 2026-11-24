# ADR-001 — Cliente móvil con React Native + Expo

- **Fecha:** 23/11/2026
- **Estado:** Aceptada (aprobada por el dueño del producto con el documento del Sprint 0)

## Contexto

RIVAL busca rivales, árbitros y canchas por cercanía, barrio o ciudad. Eso ocurre en el teléfono. El dueño ya domina React y TypeScript (proyecto FIIN).

## Opciones

| Opción | A favor | En contra |
| --- | --- | --- |
| React Native + Expo | TypeScript y React conocidos; EAS Build; actualizaciones OTA | Algunas librerías nativas requieren "dev build" |
| Flutter | Dibujo muy consistente | Dart es nuevo para el equipo; no comparte código con el panel web |
| PWA | Una sola base | Ubicación y notificaciones más limitadas en iOS [POR VERIFICAR] |

## Decisión

React Native con Expo (SDK 58) y TypeScript estricto para Android e iOS. El panel web de establecimientos y administración será React + Vite (Sprint posterior).

## Consecuencias

- Capas `src/domain`, `src/services`, `src/controllers`, `src/ui` con máximo 150 líneas por archivo.
- El token de sesión se guarda con `expo-secure-store`, nunca en AsyncStorage plano.
