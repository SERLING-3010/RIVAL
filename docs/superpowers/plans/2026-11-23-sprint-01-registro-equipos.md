# Sprint 1 — Registro por rol, equipos y Mi equipo — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** una persona se registra con su rol y sus deportes, crea un equipo o pide entrar a uno, y ve Mi equipo.

**Arquitectura:** monolito modular FastAPI (domain → persistence → services → api) con SQLite en desarrollo; app Expo + TypeScript con capas domain/services/controllers/ui.

**Stack:** Python 3.12+, FastAPI, SQLAlchemy 2, Pydantic 2, argon2-cffi, pytest; Expo SDK 58, React Native, TypeScript estricto, expo-secure-store.

**Spec:** documento de estrategia del Sprint 0 (https://claude.ai/artifact/L8a8Uxfry9atkVTWMjWXg3), secciones 4.1, 4.2, 7 y 9.3 (RIV-001 a RIV-006).

## Restricciones globales

- Máximo 150 líneas por archivo; capas domain/services/controllers/ui; cero `any`; `import type` para tipos.
- Documentación y mensajes en español; identificadores, rutas y commits en inglés.
- Solo mayores de 18 (MIN_AGE_YEARS = 18).
- Los deportes y modalidades salen de `backend/app/config/sports.json`, no del código.
- Nunca se devuelve ni se guarda la ubicación exacta: solo ciudad y barrio (texto en Sprint 1).
- Permisos verificados en el backend; la interfaz no es la seguridad.
- Contraseñas con Argon2id (memoria 19 MiB, 2 iteraciones, paralelismo 1).
- Errores: `{code, message, correlation_id}`; sin trazas ni datos internos.
- Toda acción relevante deja `audit_event` con hash SHA-256 encadenado.

## Review Focus

1. Nacido el 29 de febrero: cumple 18 el 28 de febrero o el 1 de marzo — se toma el 1 de marzo en años no bisiestos (prueba en dominio).
2. Doble clic en "Solicitar unirme": una sola solicitud pendiente (409 en la segunda).
3. Un jugador cambia el `team_id` en la URL para aprobar solicitudes de otro equipo: 403 (prueba anti-IDOR).
4. El DT sale del equipo sin capitán nombrado: se rechaza con mensaje que dice nombrar capitán primero.
5. Nombres con tildes y ñ, y correo con mayúsculas: se aceptan y el correo se compara sin distinguir mayúsculas.

---

### Tarea 1: Dominio (backend/app/domain)

**Archivos:** `roles.py`, `age_policy.py`, `sports_catalog.py`, `team_rules.py`, `errors.py`; pruebas en `backend/tests/domain/`.

**Interfaces producidas:**
- `UserRole` (PLAYER, COACH, REFEREE, VENUE_OWNER); `TeamRole` (COACH, CAPTAIN, PLAYER).
- `is_adult(birth_date: date, today: date) -> bool`.
- `SportCatalog.load(path) -> SportCatalog`; `.has_sport(code) -> bool`; `.has_modality(sport, modality) -> bool`.
- `initial_team_role(creator_role: UserRole) -> TeamRole` (COACH → COACH, otro → CAPTAIN).
- `resolve_admin(members: list[MemberView]) -> int | None` (DT si existe, si no capitán).
- `check_can_leave(member, members) -> None` lanza `DomainError("ADMIN_SUCCESSOR_REQUIRED")`.
- `DomainError(code: str, message: str)`.

- [ ] Pruebas que fallan: `test_is_adult_turns_18_on_birthday`, `test_leap_day_birthday_adult_on_march_first`, `test_admin_is_coach_when_present`, `test_admin_falls_back_to_captain`, `test_coach_cannot_leave_without_captain`, `test_catalog_rejects_unknown_sport`.
- [ ] Implementar y ver pasar con `pytest backend/tests/domain -v`.

### Tarea 2: Persistencia, servicios y auditoría

**Archivos:** `persistence/database.py`, `persistence/models_*.py`, `services/auth_service.py`, `services/team_service.py`, `services/audit_service.py`, `services/rate_limiter.py`, `services/passwords.py`.

**Interfaces producidas:** `register_user(db, RegisterInput) -> UserAccount`, `login(db, email, password, client_key) -> SessionToken`, `create_team(db, actor, CreateTeamInput)`, `request_join`, `decide_join_request`, `set_captain`, `leave_team`, `record_event(db, actor_id, action, entity, entity_id, before, after)`.

- [ ] Pruebas: registro de menor rechazado (`UNDERAGE`), correo duplicado (`EMAIL_TAKEN`), login con 5 fallos bloquea con espera creciente, cadena de auditoría verificable (`verify_chain() is True`).

### Tarea 3: API FastAPI

Rutas `/api/v1`: `GET /catalog/sports`, `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /me`, `POST /me/roles`, `POST /teams`, `GET /teams`, `GET /teams/{id}`, `GET /me/teams`, `POST /teams/{id}/join-requests`, `GET /teams/{id}/join-requests`, `POST /join-requests/{id}/approve|reject`, `POST /teams/{id}/captain`, `POST /teams/{id}/leave`.

- [ ] Pruebas de API con `TestClient`: flujo feliz completo, 401 sin token, 403 anti-IDOR, 409 doble solicitud, formato de error con `correlation_id`.

### Tarea 4: App móvil

Pantallas: elegir rol → registro → inicio por rol → buscar equipo / crear equipo → Mi equipo (plantilla, solicitudes pendientes si es administrador). Cada vista usa `ViewState` con los 7 estados.

- [ ] `npx tsc --noEmit` sin errores; ningún archivo > 150 líneas; cero `any`.

### Tarea 5: Verificación y entrega

- [ ] `pytest -v` y `npx tsc --noEmit` con salida conservada; conteo de líneas; revisión independiente; script PowerShell del Loop 5.
