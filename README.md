# RIVAL

Aplicación de deportes para equipos amateur: cada persona se registra como jugador, director técnico, árbitro o establecimiento deportivo; los equipos buscan rival por cercanía, barrio o ciudad, pactan las condiciones del partido y juegan con o sin árbitro, en canchas registradas o lugares informales.

Estado: **Sprint 2** — rivales por cercanía/barrio/ciudad, retos y ofertas, agentes libres. Ver `docs/sprint-01.md` y `docs/sprint-02.md`.

## Estructura

| Carpeta | Qué contiene |
| --- | --- |
| `backend/` | API FastAPI (Python 3.12+): `app/domain`, `app/persistence`, `app/services`, `app/api` |
| `mobile/` | App Expo + TypeScript: `src/domain`, `src/services`, `src/controllers`, `src/ui`, `src/app` |
| `docs/adr/` | Decisiones de arquitectura (ADR-001 a ADR-006) |
| `docs/superpowers/plans/` | Planes de implementación por Sprint |
| `CLAUDE.md` | Reglas del proyecto para quien programe (personas o agentes) |

## Cómo correrlo en Windows

Backend (PowerShell):

```powershell
cd backend
py -3 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m pytest -v
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

App móvil (otra ventana):

```powershell
cd mobile
npm ci
npm run typecheck
npm test
npx expo start --android
```

Con el emulador de Android, la app llega al backend por `http://10.0.2.2:8000` (valor por defecto). Para un teléfono físico ver `mobile/README.md`.

## Reglas clave

Solo mayores de 18 · nunca ubicación exacta · pagos fuera de la app · permisos verificados en el backend · auditoría con hash encadenado · máximo 150 líneas por archivo · cero `any`.
