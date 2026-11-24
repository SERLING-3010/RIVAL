<#
  RIVAL - Sprints 1 y 2 - Loop 5 (Sprint Review)

  Que hace este script:
    1. Comprueba que estas dentro de tu copia del repositorio SERLING-3010/RIVAL.
    2. Escribe los archivos del Sprint. Si un archivo ya existe y es distinto, guarda antes
       una copia "archivo.bak-AAAAMMDD-HHMMSS" (no borra nada, no usa Remove-Item).
    3. Te pregunta antes de instalar paquetes (PyPI y npm) y, si aceptas, ejecuta las pruebas.
    4. Revisa que ningun archivo de codigo pase de 150 lineas e imprime un resumen.

  No hace commit ni push: eso lo decides tu despues de revisar con "git status".

  Uso (PowerShell, dentro de la carpeta del repo):
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\rival-sprint.ps1
#>
param([string]$RepoPath = (Get-Location).Path)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Created = New-Object System.Collections.Generic.List[string]
$Replaced = New-Object System.Collections.Generic.List[string]
$Unchanged = New-Object System.Collections.Generic.List[string]

$RepoPath = (Resolve-Path $RepoPath).Path
if (-not (Test-Path (Join-Path $RepoPath '.git'))) {
  throw "No encuentro .git en $RepoPath. Ejecuta el script dentro de tu copia de RIVAL."
}
$Origin = (& git -C $RepoPath remote get-url origin) 2>$null
if ($Origin -notmatch 'SERLING-3010/RIVAL') {
  throw "El repositorio de $RepoPath no es SERLING-3010/RIVAL (origin: $Origin). No escribo nada."
}
$Pending = (& git -C $RepoPath status --porcelain)
if ($Pending) {
  Write-Host 'Aviso: tienes cambios sin confirmar. Se guardaran copias .bak de lo que se reemplace.' -ForegroundColor Yellow
}

function Save-Backup([string]$Path) {
  Copy-Item -LiteralPath $Path -Destination "$Path.bak-$Stamp"
}

function Write-RivalText([string]$Rel, [string]$Content) {
  $Path = Join-Path $RepoPath $Rel
  $Dir = Split-Path $Path -Parent
  if (-not (Test-Path $Dir)) { New-Item -ItemType Directory -Force -Path $Dir | Out-Null }
  $Content = ($Content -replace "`r`n", "`n") + "`n"
  if (Test-Path -LiteralPath $Path) {
    $Old = ([IO.File]::ReadAllText($Path)) -replace "`r`n", "`n"
    if ($Old -eq $Content) { $Unchanged.Add($Rel); return }
    Save-Backup $Path
    $Replaced.Add($Rel)
  } else {
    $Created.Add($Rel)
  }
  [IO.File]::WriteAllText($Path, $Content, $Utf8NoBom)
}

function Write-RivalBinary([string]$Rel, [string]$Base64) {
  $Path = Join-Path $RepoPath $Rel
  $Dir = Split-Path $Path -Parent
  if (-not (Test-Path $Dir)) { New-Item -ItemType Directory -Force -Path $Dir | Out-Null }
  $Bytes = [Convert]::FromBase64String($Base64)
  if (Test-Path -LiteralPath $Path) {
    $Old = [IO.File]::ReadAllBytes($Path)
    if ([Convert]::ToBase64String($Old) -eq $Base64) { $Unchanged.Add($Rel); return }
    Save-Backup $Path
    $Replaced.Add($Rel)
  } else {
    $Created.Add($Rel)
  }
  [IO.File]::WriteAllBytes($Path, $Bytes)
}

Write-Host "Escribiendo archivos en $RepoPath ..." -ForegroundColor Cyan

Write-RivalText '.gitignore' @'
# Copias de respaldo que crea el script de cada Sprint
*.bak-*
'@
Write-RivalText 'CLAUDE.md' @'
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
'@
Write-RivalText 'README.md' @'
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
'@
Write-RivalText 'backend\.gitignore' @'
venv/
.venv/
__pycache__/
*.pyc
.pytest_cache/
rival_dev.db
*.db
.env
'@
Write-RivalText 'backend\README.md' @'
# RIVAL — Backend

API FastAPI con capas:

- `app/domain`: reglas puras (edad ≥ 18, administrador del equipo, catálogo de deportes, validaciones). Sin base de datos ni HTTP.
- `app/persistence`: modelos SQLAlchemy 2. SQLite en desarrollo (ADR-003); PostgreSQL + PostGIS desde el Sprint 2.
- `app/services`: casos de uso, sesiones, límite de intentos y auditoría encadenada.
- `app/api`: rutas `/api/v1`, esquemas Pydantic (campos desconocidos se rechazan) y manejo de errores.

## Variables de entorno

| Variable | Por defecto | Uso |
| --- | --- | --- |
| `RIVAL_DATABASE_URL` | `sqlite:///./rival_dev.db` | Base de datos |
| `RIVAL_CORS_ORIGINS` | `http://localhost:8081` | Orígenes permitidos (nunca `*`) |
| `RIVAL_SESSION_TTL_HOURS` | `168` | Vida máxima de una sesión |
| `RIVAL_SESSION_IDLE_HOURS` | `72` | Cierre por inactividad |
| `RIVAL_DEBUG` | `false` | Si es `true`, publica `/docs` (solo desarrollo) |
| `RIVAL_TEST_DATABASE_URL` | SQLite en memoria | Si se define (p. ej. `postgresql+psycopg://rival:clave@127.0.0.1/rival_test`), las pruebas corren contra PostgreSQL, incluidas las de concurrencia |

## Comandos

```powershell
.\venv\Scripts\python.exe -m pytest -v
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
.\venv\Scripts\python.exe -m pip_audit -r requirements.txt   # opcional: escaneo de vulnerabilidades
```

## Catálogo de barrios (ADR-006)

La búsqueda "Cerca de mí" necesita el centro de cada barrio. Se importa desde un CSV separado por `;` con encabezado `nombre;ciudad;lat;lon;fuente`:

```powershell
.\venv\Scripts\python.exe -m app.tools.import_neighborhoods C:\ruta\barrios_barranquilla.csv
```

Fuente prevista para Barranquilla: "Mapa de Barrios de Barranquilla Según el POT" en datos.gov.co [POR VERIFICAR: convertir los polígonos a centroides]. Sin catálogo, la búsqueda por barrio y por ciudad funciona igual.

## Base de datos de desarrollo

El Sprint 2 agrega tablas y columnas. Como aún no hay migraciones versionadas (llegan antes del piloto), borra `backend\rival_dev.db` para que se cree de nuevo. Solo afecta datos de prueba.

## Endpoints del Sprint 2

`GET /api/v1/teams/{id}/rivals?scope=NEARBY|NEIGHBORHOOD|CITY&radius_km=` · `GET|POST /api/v1/me/free-agent` · `GET /api/v1/free-agents?sport=&city=&neighborhood=` · `POST /api/v1/teams/{id}/invitations` · `GET /api/v1/me/invitations` · `POST /api/v1/invitations/{id}/accept|reject` · `POST|GET /api/v1/teams/{id}/match-requests` · `GET /api/v1/teams/{id}/match-feed` · `POST /api/v1/match-requests/{id}/cancel` · `POST /api/v1/teams/{id}/match-requests/{rid}/offers` · `GET /api/v1/match-requests/{id}/offers` · `POST /api/v1/offers/{id}/accept|reject|withdraw`

## Endpoints del Sprint 1

`GET /api/v1/catalog/sports` · `POST /api/v1/auth/register` · `POST /api/v1/auth/login` · `POST /api/v1/auth/logout` · `GET /api/v1/me` · `POST /api/v1/me/roles` · `POST /api/v1/teams` · `GET /api/v1/teams` · `GET /api/v1/teams/{id}` · `GET /api/v1/me/teams` · `POST /api/v1/teams/{id}/join-requests` · `GET /api/v1/teams/{id}/join-requests` · `POST /api/v1/join-requests/{id}/approve` · `POST /api/v1/join-requests/{id}/reject` · `POST /api/v1/teams/{id}/captain` · `POST /api/v1/teams/{id}/leave`
'@
Write-RivalText 'backend\app\__init__.py' @'

'@
Write-RivalText 'backend\app\api\__init__.py' @'

'@
Write-RivalText 'backend\app\api\dependencies.py' @'
"""Dependencias de FastAPI: contexto de servicio por petición y usuario autenticado."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Header, Request

from app.domain.errors import AuthenticationError
from app.persistence.database import session_scope
from app.persistence.models_identity import UserAccount
from app.services import auth_service
from app.services.context import ServiceContext
from app.services.ip_limiter import login_ip_limiter, register_limiter
from app.services.rate_limiter import LoginRateLimiter


def get_ctx(request: Request) -> Iterator[ServiceContext]:
    state = request.app.state
    for session in session_scope(state.session_factory):
        yield ServiceContext(
            db=session,
            clock=state.clock,
            catalog=state.catalog,
            session_ttl=state.settings.session_ttl,
            session_idle=state.settings.session_idle,
        )


def get_limiter(request: Request) -> LoginRateLimiter:
    limiter: LoginRateLimiter = request.app.state.login_limiter
    return limiter


def ip_limits(request: Request) -> "IpLimits":
    limits: IpLimits = request.app.state.ip_limits
    return limits


class IpLimits:
    """Límites por IP para registro e inicio de sesión."""

    def __init__(self) -> None:
        self.register = register_limiter()
        self.login = login_ip_limiter()


def client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("SESSION_EXPIRED", "Inicia sesión para continuar.")
    return authorization.removeprefix("Bearer ").strip()


CtxDep = Annotated[ServiceContext, Depends(get_ctx)]
TokenDep = Annotated[str, Depends(bearer_token)]


def current_user(ctx: CtxDep, token: TokenDep) -> UserAccount:
    return auth_service.authenticate(ctx, token)


UserDep = Annotated[UserAccount, Depends(current_user)]
LimiterDep = Annotated[LoginRateLimiter, Depends(get_limiter)]
ClientKeyDep = Annotated[str, Depends(client_key)]
IpLimitsDep = Annotated[IpLimits, Depends(ip_limits)]
'@
Write-RivalText 'backend\app\api\errors.py' @'
"""Traducción de errores a respuestas: mensaje comprensible + correlation_id, sin trazas internas."""

import logging
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from app.domain.errors import (
    AuthenticationError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitedError,
)
from app.services.request_context import current_correlation_id, new_correlation_id

logger = logging.getLogger("rival.api")

_STATUS_BY_TYPE: list[tuple[type[DomainError], int]] = [
    (RateLimitedError, 429),
    (AuthenticationError, 401),
    (PermissionDeniedError, 403),
    (NotFoundError, 404),
    (ConflictError, 409),
]


def _body(code: str, message: str, details: list[str] | None = None) -> dict[str, object]:
    body: dict[str, object] = {"code": code, "message": message, "correlation_id": current_correlation_id()}
    if details:
        body["details"] = details
    return body


async def _domain_handler(_request: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, DomainError)
    status = next((s for t, s in _STATUS_BY_TYPE if isinstance(error, t)), 422)
    headers = {}
    if isinstance(error, RateLimitedError):
        headers["Retry-After"] = str(error.retry_after_seconds)
    return JSONResponse(_body(error.code, error.message), status_code=status, headers=headers)


async def _validation_handler(_request: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, RequestValidationError)
    fields = sorted({".".join(str(p) for p in e["loc"][1:]) or "cuerpo" for e in error.errors()})
    return JSONResponse(
        _body("VALIDATION_ERROR", "Revisa los campos marcados e inténtalo de nuevo.", fields), status_code=422
    )


async def _unexpected_handler(_request: Request, error: Exception) -> JSONResponse:
    logger.exception("Error no controlado correlation_id=%s", current_correlation_id(), exc_info=error)
    return JSONResponse(
        _body("INTERNAL_ERROR", "Algo salió mal de nuestro lado. Inténtalo de nuevo en un momento."),
        status_code=500,
    )


def install_error_handling(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_handler)
    app.add_exception_handler(RequestValidationError, _validation_handler)
    app.add_exception_handler(Exception, _unexpected_handler)

    @app.middleware("http")
    async def correlation_and_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = new_correlation_id()
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
'@
Write-RivalText 'backend\app\api\routes_auth.py' @'
"""Rutas de identidad y catálogo."""

from dataclasses import asdict

from fastapi import APIRouter, Request, Response

from app.api.dependencies import ClientKeyDep, CtxDep, IpLimitsDep, LimiterDep, TokenDep, UserDep
from app.api.schemas_auth import AddRoleRequest, LoginRequest, RegisterRequest, SessionOut, UserOut
from app.services import auth_service
from app.services.inputs import RegisterInput

router = APIRouter(prefix="/api/v1")


@router.get("/catalog/sports")
def sports_catalog(request: Request) -> dict[str, object]:
    return {"sports": [asdict(s) for s in request.app.state.catalog.sports]}


@router.post("/auth/register", status_code=201)
def register(
    body: RegisterRequest, ctx: CtxDep, limiter: LimiterDep, key: ClientKeyDep, ip: IpLimitsDep
) -> SessionOut:
    ip.register.hit(key, ctx.clock.now())
    auth_service.register_user(ctx, RegisterInput(**body.model_dump()))
    token, user = auth_service.login(ctx, limiter, body.email, body.password, key)
    return SessionOut(token=token, user=UserOut.from_account(user))


@router.post("/auth/login")
def login(body: LoginRequest, ctx: CtxDep, limiter: LimiterDep, key: ClientKeyDep, ip: IpLimitsDep) -> SessionOut:
    ip.login.hit(key, ctx.clock.now())
    token, user = auth_service.login(ctx, limiter, body.email, body.password, key)
    return SessionOut(token=token, user=UserOut.from_account(user))


@router.post("/auth/logout", status_code=204)
def logout(ctx: CtxDep, token: TokenDep) -> Response:
    auth_service.logout(ctx, token)
    return Response(status_code=204)


@router.get("/me")
def me(user: UserDep) -> UserOut:
    return UserOut.from_account(user)


@router.post("/me/roles")
def add_role(body: AddRoleRequest, ctx: CtxDep, user: UserDep) -> UserOut:
    return UserOut.from_account(auth_service.add_role(ctx, user, body.role, body.sports))
'@
Write-RivalText 'backend\app\api\routes_matches.py' @'
"""Rutas de búsquedas de partido (abiertas o retos) y ofertas."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import CtxDep, UserDep
from app.api.routes_scouting import SearchUser
from app.api.schemas_scouting import MatchRequestBody, MatchRequestOut, OfferBody, OfferOut
from app.domain.geo import DEFAULT_RADIUS_KM, SearchScope
from app.services import match_feed_service, match_offer_service, match_request_service
from app.services.match_request_service import to_view
from app.services.match_views import MatchRequestInput, OfferInput

router = APIRouter(prefix="/api/v1")


def _status(item: object) -> dict[str, object]:
    return {"id": getattr(item, "id"), "status": getattr(item, "status")}


@router.post("/teams/{team_id}/match-requests", status_code=201)
def create_request(team_id: int, body: MatchRequestBody, ctx: CtxDep, user: UserDep) -> MatchRequestOut:
    data = MatchRequestInput(**{**body.model_dump(), "scope": SearchScope(body.scope)})
    request = match_request_service.create_request(ctx, user, team_id, data)
    return MatchRequestOut.model_validate(asdict(to_view(ctx, request)))


@router.get("/teams/{team_id}/match-requests")
def team_requests(team_id: int, ctx: CtxDep, user: UserDep) -> list[MatchRequestOut]:
    return [MatchRequestOut.model_validate(asdict(v)) for v in match_request_service.team_requests(ctx, user, team_id)]


@router.get("/teams/{team_id}/match-feed")
def match_feed(
    team_id: int, ctx: CtxDep, user: SearchUser,
    scope: SearchScope = SearchScope.CITY,
    radius_km: Annotated[int, Query(ge=1, le=15)] = DEFAULT_RADIUS_KM,
) -> list[MatchRequestOut]:
    views = match_feed_service.open_requests_for(ctx, user, team_id, scope, radius_km)
    return [MatchRequestOut.model_validate(asdict(v)) for v in views]


@router.post("/match-requests/{request_id}/cancel")
def cancel_request(request_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    return _status(match_request_service.cancel_request(ctx, user, request_id))


@router.post("/teams/{team_id}/match-requests/{request_id}/offers", status_code=201)
def make_offer(team_id: int, request_id: int, body: OfferBody, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    offer = match_offer_service.make_offer(ctx, user, team_id, request_id, OfferInput(**body.model_dump()))
    return {**_status(offer), "version": offer.version}


@router.get("/match-requests/{request_id}/offers")
def list_offers(request_id: int, ctx: CtxDep, user: UserDep) -> list[OfferOut]:
    return [OfferOut.model_validate(asdict(v)) for v in match_offer_service.list_offers(ctx, user, request_id)]


@router.post("/offers/{offer_id}/accept")
def accept_offer(offer_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    return _status(match_offer_service.decide(ctx, user, offer_id, accept=True))


@router.post("/offers/{offer_id}/reject")
def reject_offer(offer_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    return _status(match_offer_service.decide(ctx, user, offer_id, accept=False))


@router.post("/offers/{offer_id}/withdraw")
def withdraw_offer(offer_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    return _status(match_offer_service.withdraw(ctx, user, offer_id))
'@
Write-RivalText 'backend\app\api\routes_scouting.py' @'
"""Rutas de rivales, agentes libres e invitaciones. Las búsquedas tienen límite por usuario."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_scouting import (
    FreeAgentPageOut,
    FreeAgentProfileOut,
    FreeAgentRequest,
    InvitationOut,
    InviteRequest,
    RivalPageOut,
)
from app.domain.geo import DEFAULT_RADIUS_KM, SearchScope
from app.persistence.models_identity import UserAccount
from app.services import free_agent_service, invitation_service, rival_service

router = APIRouter(prefix="/api/v1")


def search_quota(request: Request, ctx: CtxDep, user: UserDep) -> UserAccount:
    """Máximo de búsquedas por usuario: evita adivinar dónde juega un equipo con muchas consultas."""
    request.app.state.search_limiter.hit(f"user:{user.id}", ctx.clock.now())
    return user


SearchUser = Annotated[UserAccount, Depends(search_quota)]


@router.get("/teams/{team_id}/rivals")
def rivals(
    team_id: int, ctx: CtxDep, user: SearchUser,
    scope: SearchScope = SearchScope.CITY,
    radius_km: Annotated[int, Query(ge=1, le=15)] = DEFAULT_RADIUS_KM,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
) -> RivalPageOut:
    result = rival_service.search_rivals(ctx, user, team_id, scope, radius_km, page)
    return RivalPageOut.model_validate(asdict(result))


@router.get("/me/free-agent")
def my_free_agent(ctx: CtxDep, user: UserDep) -> list[FreeAgentProfileOut]:
    return [FreeAgentProfileOut.model_validate(p, from_attributes=True)
            for p in free_agent_service.my_profiles(ctx, user)]


@router.post("/me/free-agent")
def set_free_agent(body: FreeAgentRequest, ctx: CtxDep, user: UserDep) -> FreeAgentProfileOut:
    profile = free_agent_service.set_free_agent(ctx, user, body.sport_code, body.active, body.position, body.note)
    return FreeAgentProfileOut.model_validate(profile, from_attributes=True)


@router.get("/free-agents")
def free_agents(
    ctx: CtxDep, user: SearchUser,
    sport: Annotated[str, Query(max_length=30)],
    city: Annotated[str, Query(max_length=60)],
    neighborhood: Annotated[str | None, Query(max_length=60)] = None,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
) -> FreeAgentPageOut:
    result = free_agent_service.search(ctx, user, sport, city, neighborhood, page)
    return FreeAgentPageOut.model_validate(asdict(result))


@router.post("/teams/{team_id}/invitations", status_code=201)
def invite(team_id: int, body: InviteRequest, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    invitation = invitation_service.invite(ctx, user, team_id, body.user_id, body.message)
    return {"id": invitation.id, "status": invitation.status}


@router.get("/me/invitations")
def my_invitations(ctx: CtxDep, user: UserDep) -> list[InvitationOut]:
    return [InvitationOut.model_validate(asdict(v)) for v in invitation_service.my_invitations(ctx, user)]


@router.post("/invitations/{invitation_id}/accept")
def accept_invitation(invitation_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    invitation = invitation_service.respond(ctx, user, invitation_id, accept=True)
    return {"id": invitation.id, "status": invitation.status}


@router.post("/invitations/{invitation_id}/reject")
def reject_invitation(invitation_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    invitation = invitation_service.respond(ctx, user, invitation_id, accept=False)
    return {"id": invitation.id, "status": invitation.status}
'@
Write-RivalText 'backend\app\api\routes_teams.py' @'
"""Rutas de equipos, solicitudes de unión y plantilla. Los permisos se verifican en los servicios."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_teams import (
    CreateTeamRequest,
    JoinRequestBody,
    JoinRequestOut,
    MyTeamOut,
    SetCaptainRequest,
    TeamDetailOut,
    TeamPageOut,
)
from app.services import join_service, membership_service, team_service
from app.services.inputs import CreateTeamInput, JoinRequestInput, TeamSearchInput

router = APIRouter(prefix="/api/v1")


def _detail(ctx: CtxDep, team_id: int) -> TeamDetailOut:
    return TeamDetailOut.model_validate(asdict(team_service.team_detail(ctx, team_id)))


@router.post("/teams", status_code=201)
def create_team(body: CreateTeamRequest, ctx: CtxDep, user: UserDep) -> TeamDetailOut:
    team = team_service.create_team(ctx, user, CreateTeamInput(**body.model_dump()))
    return _detail(ctx, team.id)


@router.get("/teams")
def search_teams(
    ctx: CtxDep,
    _user: UserDep,
    sport: Annotated[str | None, Query(max_length=30)] = None,
    modality: Annotated[str | None, Query(max_length=30)] = None,
    city: Annotated[str | None, Query(max_length=60)] = None,
    q: Annotated[str | None, Query(max_length=60)] = None,
    page: Annotated[int, Query(ge=1, le=10_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
) -> TeamPageOut:
    query = TeamSearchInput(sport_code=sport, modality_code=modality, city=city, query=q, page=page, page_size=page_size)
    return TeamPageOut.model_validate(asdict(team_service.search_teams(ctx, query)))


@router.get("/teams/{team_id}")
def team_detail(team_id: int, ctx: CtxDep, _user: UserDep) -> TeamDetailOut:
    return _detail(ctx, team_id)


@router.get("/me/teams")
def my_teams(ctx: CtxDep, user: UserDep) -> list[MyTeamOut]:
    return [MyTeamOut.model_validate(asdict(view)) for view in team_service.my_teams(ctx, user)]


@router.post("/teams/{team_id}/join-requests", status_code=201)
def request_join(team_id: int, body: JoinRequestBody, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    request = join_service.request_join(ctx, user, team_id, JoinRequestInput(**body.model_dump()))
    return {"id": request.id, "status": request.status}


@router.get("/teams/{team_id}/join-requests")
def list_join_requests(team_id: int, ctx: CtxDep, user: UserDep) -> list[JoinRequestOut]:
    return [JoinRequestOut.model_validate(asdict(v)) for v in join_service.list_requests(ctx, user, team_id)]


@router.post("/join-requests/{request_id}/approve")
def approve(request_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    request = join_service.decide(ctx, user, request_id, approve=True)
    return {"id": request.id, "status": request.status}


@router.post("/join-requests/{request_id}/reject")
def reject(request_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    request = join_service.decide(ctx, user, request_id, approve=False)
    return {"id": request.id, "status": request.status}


@router.post("/teams/{team_id}/captain")
def set_captain(team_id: int, body: SetCaptainRequest, ctx: CtxDep, user: UserDep) -> TeamDetailOut:
    membership_service.set_captain(ctx, user, team_id, body.user_id)
    return _detail(ctx, team_id)


@router.post("/teams/{team_id}/leave", status_code=204)
def leave(team_id: int, ctx: CtxDep, user: UserDep) -> Response:
    membership_service.leave_team(ctx, user, team_id)
    return Response(status_code=204)
'@
Write-RivalText 'backend\app\api\schemas_auth.py' @'
"""Esquemas de entrada y salida de identidad. Campos desconocidos se rechazan."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.domain.roles import UserRole
from app.persistence.models_identity import UserAccount


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_max_length=254)


class RegisterRequest(StrictModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)
    display_name: str = Field(max_length=60)
    birth_date: date
    role: UserRole
    sports: list[str] = Field(min_length=1, max_length=10)
    city: str = Field(max_length=60)
    neighborhood: str = Field(max_length=60)
    position: str | None = Field(default=None, max_length=40)


class LoginRequest(StrictModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class AddRoleRequest(StrictModel):
    role: UserRole
    sports: list[str] = Field(min_length=1, max_length=10)


class UserOut(BaseModel):
    id: int
    email: str
    display_name: str
    roles: list[UserRole]
    sports: list[str]
    city: str
    neighborhood: str
    position: str | None

    @classmethod
    def from_account(cls, user: UserAccount) -> "UserOut":
        return cls(
            id=user.id, email=user.email, display_name=user.display_name,
            roles=[UserRole(r.role) for r in user.roles],
            sports=sorted(s.sport_code for s in user.sports),
            city=user.city, neighborhood=user.neighborhood, position=user.position,
        )


class SessionOut(BaseModel):
    token: str
    user: UserOut
'@
Write-RivalText 'backend\app\api\schemas_scouting.py' @'
"""Esquemas de rivales, agentes libres, invitaciones y partidos (Sprint 2)."""

from pydantic import AwareDatetime, BaseModel, Field

from app.api.schemas_auth import StrictModel
from app.api.schemas_teams import TeamSummaryOut
from app.domain.geo import DistanceBand
from app.domain.match_rules import PlaceKind, RefereeMode


class RivalOut(BaseModel):
    team: TeamSummaryOut
    distance_band: DistanceBand | None


class RivalPageOut(BaseModel):
    items: list[RivalOut]
    page: int
    page_size: int
    total: int


class FreeAgentRequest(StrictModel):
    sport_code: str = Field(max_length=30)
    active: bool
    position: str | None = Field(default=None, max_length=40)
    note: str | None = Field(default=None, max_length=200)


class FreeAgentProfileOut(BaseModel):
    sport_code: str
    active: bool
    position: str | None
    note: str | None


class FreeAgentOut(BaseModel):
    user_id: int
    display_name: str
    sport_code: str
    position: str | None
    note: str | None
    neighborhood: str
    city: str


class FreeAgentPageOut(BaseModel):
    items: list[FreeAgentOut]
    page: int
    page_size: int
    total: int


class InviteRequest(StrictModel):
    user_id: int
    message: str | None = Field(default=None, max_length=200)


class InvitationOut(BaseModel):
    id: int
    team: TeamSummaryOut
    message: str | None


class MatchRequestBody(StrictModel):
    window_start: AwareDatetime
    window_end: AwareDatetime
    scope: str = Field(pattern="^(NEARBY|NEIGHBORHOOD|CITY)$")
    radius_km: int | None = Field(default=None, ge=1, le=15)
    target_team_id: int | None = None
    referee_mode: RefereeMode
    place_kind: PlaceKind
    place_note: str | None = Field(default=None, max_length=120)
    message: str | None = Field(default=None, max_length=200)


class OfferBody(StrictModel):
    proposed_start: AwareDatetime
    referee_mode: RefereeMode
    place_kind: PlaceKind
    place_note: str | None = Field(default=None, max_length=120)
    message: str | None = Field(default=None, max_length=200)


class MatchRequestOut(BaseModel):
    id: int
    team: TeamSummaryOut
    target_team_id: int | None
    scope: str
    radius_km: int | None
    window_start: AwareDatetime
    window_end: AwareDatetime
    referee_mode: str
    place_kind: str
    place_note: str | None
    message: str | None
    status: str
    distance_band: DistanceBand | None
    pending_offers: int
    accepted_offer_id: int | None


class OfferOut(BaseModel):
    id: int
    request_id: int
    team: TeamSummaryOut
    version: int
    proposed_start: AwareDatetime
    referee_mode: str
    place_kind: str
    place_note: str | None
    message: str | None
    status: str
'@
Write-RivalText 'backend\app\api\schemas_teams.py' @'
"""Esquemas de equipos y solicitudes."""

from pydantic import BaseModel, Field

from app.api.schemas_auth import StrictModel
from app.domain.roles import TeamRole


class CreateTeamRequest(StrictModel):
    name: str = Field(max_length=60)
    sport_code: str = Field(max_length=30)
    modality_code: str = Field(max_length=30)
    city: str = Field(max_length=60)
    neighborhood: str = Field(max_length=60)
    as_coach: bool = False


class JoinRequestBody(StrictModel):
    desired_role: TeamRole = TeamRole.PLAYER
    message: str | None = Field(default=None, max_length=200)


class SetCaptainRequest(StrictModel):
    user_id: int


class TeamSummaryOut(BaseModel):
    id: int
    name: str
    sport_code: str
    modality_code: str
    city: str
    neighborhood: str
    member_count: int
    has_coach: bool


class MemberOut(BaseModel):
    user_id: int
    display_name: str
    role: TeamRole
    position: str | None


class TeamDetailOut(BaseModel):
    team: TeamSummaryOut
    admin_user_id: int | None
    members: list[MemberOut]


class MyTeamOut(BaseModel):
    team: TeamSummaryOut
    my_role: TeamRole
    is_admin: bool
    pending_requests: int


class TeamPageOut(BaseModel):
    items: list[TeamSummaryOut]
    page: int
    page_size: int
    total: int


class JoinRequestOut(BaseModel):
    id: int
    team_id: int
    user_id: int
    display_name: str
    position: str | None
    desired_role: TeamRole
    message: str | None
    status: str
'@
Write-RivalText 'backend\app\config\sports.json' @'
{
  "version": "2026-11-23",
  "sports": [
    {
      "code": "FOOTBALL",
      "name": "Fútbol",
      "modalities": [
        {"code": "F5", "name": "Fútbol 5", "players_per_side": 5},
        {"code": "F7", "name": "Fútbol 7", "players_per_side": 7},
        {"code": "F8", "name": "Fútbol 8", "players_per_side": 8},
        {"code": "F11", "name": "Fútbol 11", "players_per_side": 11}
      ]
    },
    {
      "code": "FUTSAL",
      "name": "Microfútbol",
      "modalities": [
        {"code": "MICRO5", "name": "Microfútbol 5", "players_per_side": 5}
      ]
    },
    {
      "code": "BASKETBALL",
      "name": "Baloncesto",
      "modalities": [
        {"code": "B3X3", "name": "Baloncesto 3x3", "players_per_side": 3},
        {"code": "B5X5", "name": "Baloncesto 5x5", "players_per_side": 5}
      ]
    },
    {
      "code": "BASEBALL",
      "name": "Béisbol",
      "modalities": [
        {"code": "BASEBALL9", "name": "Béisbol", "players_per_side": 9},
        {"code": "SOFTBALL", "name": "Softbol", "players_per_side": 9}
      ]
    },
    {
      "code": "VOLLEYBALL",
      "name": "Voleibol",
      "modalities": [
        {"code": "V6", "name": "Voleibol 6", "players_per_side": 6},
        {"code": "BEACH2", "name": "Voleibol playa 2x2", "players_per_side": 2}
      ]
    }
  ]
}
'@
Write-RivalText 'backend\app\domain\__init__.py' @'

'@
Write-RivalText 'backend\app\domain\age_policy.py' @'
"""Política de edad: RIVAL es solo para mayores de 18 (decisión del dueño, 23/11/2026)."""

from datetime import date

MIN_AGE_YEARS = 18


def _birthday_in_year(birth_date: date, year: int) -> date:
    """Cumpleaños en un año dado. Un 29 de febrero cumple el 1 de marzo en años no bisiestos.

    [SUPUESTO] Regla conservadora: nadie se considera adulto antes de tiempo.
    """
    try:
        return birth_date.replace(year=year)
    except ValueError:
        return date(year, 3, 1)


def is_adult(birth_date: date, today: date) -> bool:
    """True si la persona ya cumplió MIN_AGE_YEARS en la fecha `today`."""
    if birth_date > today:
        return False
    coming_of_age = _birthday_in_year(birth_date, birth_date.year + MIN_AGE_YEARS)
    return today >= coming_of_age
'@
Write-RivalText 'backend\app\domain\errors.py' @'
"""Errores de dominio con código estable y mensaje en español para el usuario."""


class DomainError(Exception):
    """Regla de negocio violada. El código es estable; el mensaje es para personas."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class NotFoundError(DomainError):
    """El recurso no existe o el actor no puede verlo."""


class PermissionDeniedError(DomainError):
    """El actor no tiene permiso para esta acción."""


class ConflictError(DomainError):
    """La acción choca con el estado actual (duplicado, ya resuelto, etc.)."""


class AuthenticationError(DomainError):
    """Credenciales o sesión inválidas."""


class RateLimitedError(DomainError):
    """Demasiados intentos; hay que esperar."""

    def __init__(self, code: str, message: str, retry_after_seconds: int) -> None:
        super().__init__(code, message)
        self.retry_after_seconds = retry_after_seconds
'@
Write-RivalText 'backend\app\domain\geo.py' @'
"""Distancias entre centros de barrio (ADR-006). Nunca se usan posiciones de personas.

Las coordenadas son float porque no son dinero; a las personas solo se les muestra un rango.
"""

import math
from enum import StrEnum

from app.domain.errors import DomainError

EARTH_RADIUS_KM = 6371.0
MIN_RADIUS_KM = 1
MAX_RADIUS_KM = 15
DEFAULT_RADIUS_KM = 5


class DistanceBand(StrEnum):
    UNDER_2_KM = "UNDER_2_KM"
    FROM_2_TO_5_KM = "FROM_2_TO_5_KM"
    OVER_5_KM = "OVER_5_KM"


class SearchScope(StrEnum):
    NEARBY = "NEARBY"
    NEIGHBORHOOD = "NEIGHBORHOOD"
    CITY = "CITY"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def distance_band(km: float) -> DistanceBand:
    if km < 2:
        return DistanceBand.UNDER_2_KM
    if km <= 5:
        return DistanceBand.FROM_2_TO_5_KM
    return DistanceBand.OVER_5_KM


def validate_radius_km(radius_km: int) -> int:
    if not MIN_RADIUS_KM <= radius_km <= MAX_RADIUS_KM:
        raise DomainError(
            "INVALID_RADIUS", f"El radio debe estar entre {MIN_RADIUS_KM} y {MAX_RADIUS_KM} km."
        )
    return radius_km


def validate_coordinates(lat: float, lon: float) -> None:
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise DomainError("INVALID_COORDINATES", "Coordenadas fuera de rango.")
'@
Write-RivalText 'backend\app\domain\identity_rules.py' @'
"""Validaciones de identidad: correo, nombre visible, contraseña y lugares (ciudad, barrio).

Se valida y se rechaza; nunca se altera en silencio lo que escribió la persona
(solo se quitan espacios al inicio y al final y el correo pasa a minúsculas).
"""

import re

from app.domain.errors import DomainError

MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128
COMMON_PASSWORDS: frozenset[str] = frozenset(
    {
        "1234567890",
        "12345678910",
        "contraseña123",
        "contrasena123",
        "password123",
        "qwertyuiop",
        "futbol12345",
        "colombia123",
    }
)
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NAME_PATTERN = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]{2,60}$")
_PLACE_PATTERN = re.compile(r"^[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .,#-]{2,60}$")


def normalize_email(email: str) -> str:
    cleaned = email.strip().lower()
    if len(cleaned) > 254 or not _EMAIL_PATTERN.match(cleaned):
        raise DomainError("INVALID_EMAIL", "Escribe un correo válido, por ejemplo nombre@correo.com.")
    return cleaned


def validate_display_name(name: str) -> str:
    cleaned = name.strip()
    if not _NAME_PATTERN.match(cleaned):
        raise DomainError(
            "INVALID_NAME",
            "El nombre debe tener entre 2 y 60 letras; se permiten tildes, ñ, espacios y guiones.",
        )
    return cleaned


def validate_password(password: str) -> None:
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise DomainError(
            "WEAK_PASSWORD",
            f"La contraseña debe tener entre {MIN_PASSWORD_LENGTH} y {MAX_PASSWORD_LENGTH} caracteres.",
        )
    if password.lower() in COMMON_PASSWORDS:
        raise DomainError("WEAK_PASSWORD", "Esa contraseña es muy común. Prueba con una frase.")


def validate_place_name(value: str, field: str) -> str:
    cleaned = value.strip()
    if not _PLACE_PATTERN.match(cleaned):
        raise DomainError("INVALID_PLACE", f"Escribe un nombre de {field} válido (2 a 60 caracteres).")
    return cleaned
'@
Write-RivalText 'backend\app\domain\match_rules.py' @'
"""Reglas de solicitudes de partido y ofertas (Sprint 2).

Las fechas se comparan con zona horaria. El árbitro es opcional (decisión del dueño, 23/11/2026)
y el lugar puede ser un establecimiento, un lugar informal (parque) o quedar por acordar.
"""

from datetime import datetime, timedelta
from enum import StrEnum

from app.domain.errors import DomainError

MAX_WINDOW = timedelta(days=14)
MAX_AHEAD = timedelta(days=60)
MAX_OPEN_REQUESTS_PER_TEAM = 3


class RefereeMode(StrEnum):
    WITH = "WITH"
    WITHOUT = "WITHOUT"
    EITHER = "EITHER"


class PlaceKind(StrEnum):
    VENUE = "VENUE"
    INFORMAL = "INFORMAL"
    TO_AGREE = "TO_AGREE"


class RequestStatus(StrEnum):
    OPEN = "OPEN"
    MATCHED = "MATCHED"
    CANCELLED = "CANCELLED"


class OfferStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    SUPERSEDED = "SUPERSEDED"
    CANCELLED = "CANCELLED"


def validate_window(start: datetime, end: datetime, now: datetime) -> None:
    if start < now:
        raise DomainError("WINDOW_IN_PAST", "La fecha de inicio ya pasó. Elige una fecha futura.")
    if end <= start:
        raise DomainError("WINDOW_INVERTED", "La fecha final debe ser posterior a la inicial.")
    if end - start > MAX_WINDOW:
        raise DomainError("WINDOW_TOO_LONG", "La ventana para jugar puede durar máximo 14 días.")
    if start - now > MAX_AHEAD:
        raise DomainError("WINDOW_TOO_FAR", "Solo se pueden buscar partidos en los próximos 60 días.")


def check_proposed_start(proposed: datetime, start: datetime, end: datetime, now: datetime) -> None:
    if proposed < now:
        raise DomainError("OFFER_IN_PAST", "La hora propuesta ya pasó. Propón una hora futura.")
    if not start <= proposed <= end:
        raise DomainError("OFFER_OUTSIDE_WINDOW", "La hora propuesta debe estar dentro de la ventana del rival.")


def check_offer_referee(requested: RefereeMode, offered: RefereeMode) -> None:
    if offered == RefereeMode.EITHER:
        raise DomainError("REFEREE_MODE_REQUIRED", "En la oferta indica si el partido es con o sin árbitro.")
    if requested != RefereeMode.EITHER and requested != offered:
        raise DomainError(
            "REFEREE_MODE_MISMATCH",
            "El rival pidió un partido " + ("con árbitro." if requested == RefereeMode.WITH else "sin árbitro."),
        )
'@
Write-RivalText 'backend\app\domain\roles.py' @'
"""Roles de la cuenta (cómo se registra la persona) y roles dentro de un equipo."""

from enum import StrEnum


class UserRole(StrEnum):
    PLAYER = "PLAYER"
    COACH = "COACH"
    REFEREE = "REFEREE"
    VENUE_OWNER = "VENUE_OWNER"


class TeamRole(StrEnum):
    COACH = "COACH"
    CAPTAIN = "CAPTAIN"
    PLAYER = "PLAYER"


ROLES_THAT_CAN_CREATE_TEAMS: frozenset[UserRole] = frozenset({UserRole.PLAYER, UserRole.COACH})
'@
Write-RivalText 'backend\app\domain\sports_catalog.py' @'
"""Catálogo de deportes y modalidades. Se carga de configuración, no está fijo en el código."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Modality:
    code: str
    name: str
    players_per_side: int


@dataclass(frozen=True)
class Sport:
    code: str
    name: str
    modalities: tuple[Modality, ...]


@dataclass(frozen=True)
class SportCatalog:
    sports: tuple[Sport, ...]

    @classmethod
    def load(cls, path: Path) -> "SportCatalog":
        raw = json.loads(path.read_text(encoding="utf-8"))
        sports = tuple(
            Sport(
                code=item["code"],
                name=item["name"],
                modalities=tuple(Modality(**m) for m in item["modalities"]),
            )
            for item in raw["sports"]
        )
        return cls(sports=sports)

    def has_sport(self, code: str) -> bool:
        return any(s.code == code for s in self.sports)

    def has_modality(self, sport_code: str, modality_code: str) -> bool:
        for sport in self.sports:
            if sport.code == sport_code:
                return any(m.code == modality_code for m in sport.modalities)
        return False
'@
Write-RivalText 'backend\app\domain\team_rules.py' @'
"""Reglas de administración de equipos.

El administrador no se guarda: se calcula. Es el DT si existe; si no, el capitán.
Así el equipo nunca puede quedar con dos administradores.
"""

from dataclasses import dataclass

from app.domain.errors import DomainError
from app.domain.roles import TeamRole, UserRole


@dataclass(frozen=True)
class MemberView:
    user_id: int
    role: TeamRole


def initial_team_role(creator_role: UserRole) -> TeamRole:
    """Quien crea el equipo: el DT entra como DT; cualquier otro, como capitán."""
    return TeamRole.COACH if creator_role == UserRole.COACH else TeamRole.CAPTAIN


def resolve_admin(members: list[MemberView]) -> int | None:
    """Devuelve el user_id del administrador activo, o None si no hay DT ni capitán."""
    for wanted in (TeamRole.COACH, TeamRole.CAPTAIN):
        for member in members:
            if member.role == wanted:
                return member.user_id
    return None


def check_can_leave(user_id: int, members: list[MemberView]) -> None:
    """Impide que el equipo quede sin administrador cuando todavía tiene jugadores."""
    if not any(m.user_id == user_id for m in members):
        raise DomainError("NOT_A_MEMBER", "No perteneces a este equipo.")
    remaining = [m for m in members if m.user_id != user_id]
    if not remaining:
        return
    if resolve_admin(members) != user_id:
        return
    if resolve_admin(remaining) is None:
        raise DomainError(
            "ADMIN_SUCCESSOR_REQUIRED",
            "Antes de salir, nombra un capitán para que el equipo no quede sin administrador.",
        )
'@
Write-RivalText 'backend\app\domain\text_keys.py' @'
"""Claves de búsqueda: "Bogotá", "BOGOTA" y "bogota" encuentran lo mismo."""

import unicodedata


def search_key(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.strip())
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(without_accents.casefold().split())
'@
Write-RivalText 'backend\app\main.py' @'
"""Punto de entrada de la API de RIVAL.

Desarrollo local:  uvicorn app.main:app --host 127.0.0.1 --port 8000
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_auth, routes_matches, routes_scouting, routes_teams
from app.api.dependencies import IpLimits
from app.api.errors import install_error_handling
from app.domain.sports_catalog import SportCatalog
from app.persistence.database import create_schema, make_engine, make_session_factory
from app.services.clock import SystemClock
from app.services.ip_limiter import search_limiter
from app.services.rate_limiter import LoginRateLimiter
from app.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    engine = make_engine(config.database_url)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        create_schema(engine)
        yield
        engine.dispose()

    app = FastAPI(
        title="RIVAL API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if config.debug else None,
        redoc_url=None,
        openapi_url="/openapi.json" if config.debug else None,
    )
    app.state.settings = config
    app.state.session_factory = make_session_factory(engine)
    app.state.catalog = SportCatalog.load(config.catalog_path)
    app.state.clock = SystemClock()
    app.state.login_limiter = LoginRateLimiter()
    app.state.ip_limits = IpLimits()
    app.state.search_limiter = search_limiter()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
    install_error_handling(app)
    app.include_router(routes_auth.router)
    app.include_router(routes_teams.router)
    app.include_router(routes_scouting.router)
    app.include_router(routes_matches.router)
    return app


app = create_app()
'@
Write-RivalText 'backend\app\persistence\__init__.py' @'

'@
Write-RivalText 'backend\app\persistence\database.py' @'
"""Motor y sesiones de base de datos (SQLAlchemy 2)."""

from collections.abc import Iterator
from datetime import UTC, datetime

from sqlalchemy import DateTime, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import TypeDecorator


class UtcDateTime(TypeDecorator[datetime]):
    """Guarda siempre en UTC y devuelve fechas con zona horaria (SQLite las pierde)."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: object) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Se requiere una fecha con zona horaria")
        return value.astimezone(UTC)

    def process_result_value(self, value: datetime | None, dialect: object) -> datetime | None:
        if value is None:
            return None
        return value if value.tzinfo else value.replace(tzinfo=UTC)


class Base(DeclarativeBase):
    pass


def make_engine(database_url: str) -> Engine:
    if database_url.startswith("sqlite"):
        options: dict[str, object] = {"connect_args": {"check_same_thread": False}}
        if ":memory:" in database_url:
            options["poolclass"] = StaticPool
        engine = create_engine(database_url, **options)
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
        return engine
    return create_engine(database_url, pool_pre_ping=True)


def _enable_sqlite_foreign_keys(dbapi_connection: object, _record: object) -> None:
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def load_models() -> None:
    """Registra todas las tablas en Base.metadata."""
    from app.persistence import (  # noqa: F401
        models_audit,
        models_identity,
        models_matches,
        models_places,
        models_scouting,
        models_teams,
    )


def create_schema(engine: Engine) -> None:
    from app.persistence import models_audit

    load_models()
    Base.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        if session.get(models_audit.AuditHead, 1) is None:
            session.add(models_audit.AuditHead(id=1, last_hash="0" * 64, last_position=0))


def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Una transacción por petición: confirma si todo salió bien, deshace si hubo error."""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
'@
Write-RivalText 'backend\app\persistence\models_audit.py' @'
"""Bitácora de auditoría nominal con hash encadenado (resistente a manipulación, no inmutable)."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class AuditEvent(Base):
    __tablename__ = "audit_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    chain_position: Mapped[int] = mapped_column(unique=True)
    occurred_at: Mapped[datetime] = mapped_column(UtcDateTime)
    actor_type: Mapped[str] = mapped_column(String(20))
    initiated_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(60), index=True)
    entity: Mapped[str] = mapped_column(String(40), index=True)
    entity_id: Mapped[str] = mapped_column(String(40), index=True)
    before_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(64))
    software_version: Mapped[str] = mapped_column(String(20))
    # UNIQUE: si dos escrituras leyeran el mismo eslabón, la segunda falla en vez de bifurcar la cadena.
    prev_hash: Mapped[str] = mapped_column(String(64), unique=True)
    integrity_hash: Mapped[str] = mapped_column(String(64))


class AuditHead(Base):
    """Fila única con el último eslabón. Se bloquea (FOR UPDATE) para escribir la cadena en serie."""

    __tablename__ = "audit_head"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_hash: Mapped[str] = mapped_column(String(64))
    last_position: Mapped[int] = mapped_column(default=0)
'@
Write-RivalText 'backend\app\persistence\models_identity.py' @'
"""Tablas de identidad: cuentas, roles, deportes y sesiones."""

from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.database import Base, UtcDateTime


class UserAccount(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(60))
    birth_date: Mapped[date] = mapped_column(Date)
    city: Mapped[str] = mapped_column(String(60))
    city_key: Mapped[str] = mapped_column(String(60), index=True)
    neighborhood: Mapped[str] = mapped_column(String(60))
    neighborhood_key: Mapped[str] = mapped_column(String(60))
    position: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)

    roles: Mapped[list["UserRoleRow"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    sports: Mapped[list["UserSport"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class UserRoleRow(Base):
    __tablename__ = "user_role"
    __table_args__ = (UniqueConstraint("user_id", "role"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)

    user: Mapped[UserAccount] = relationship(back_populates="roles")


class UserSport(Base):
    __tablename__ = "user_sport"
    __table_args__ = (UniqueConstraint("user_id", "sport_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"))
    sport_code: Mapped[str] = mapped_column(String(30))

    user: Mapped[UserAccount] = relationship(back_populates="sports")


class AuthSession(Base):
    """Sesión emitida por el servidor. Se guarda el hash del token, nunca el token."""

    __tablename__ = "auth_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    last_seen_at: Mapped[datetime] = mapped_column(UtcDateTime)
    expires_at: Mapped[datetime] = mapped_column(UtcDateTime)
'@
Write-RivalText 'backend\app\persistence\models_matches.py' @'
"""Solicitudes de partido (abiertas o retos directos) y ofertas de los rivales.

Una oferta nunca se edita: una contraoferta del mismo equipo crea una versión nueva
y deja la anterior como SUPERSEDED. Al aceptar una oferta la solicitud pasa a MATCHED;
el contrato con firmas llega en el Sprint 3.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class MatchRequest(Base):
    __tablename__ = "match_request"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    target_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True, index=True)
    sport_code: Mapped[str] = mapped_column(String(30))
    modality_code: Mapped[str] = mapped_column(String(30))
    scope: Mapped[str] = mapped_column(String(20))
    radius_km: Mapped[int | None] = mapped_column(nullable=True)
    window_start: Mapped[datetime] = mapped_column(UtcDateTime)
    window_end: Mapped[datetime] = mapped_column(UtcDateTime, index=True)
    referee_mode: Mapped[str] = mapped_column(String(20))
    place_kind: Mapped[str] = mapped_column(String(20))
    place_note: Mapped[str | None] = mapped_column(String(120), nullable=True)
    message: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", index=True)
    accepted_offer_id: Mapped[int | None] = mapped_column(nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    closed_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)


class MatchOffer(Base):
    __tablename__ = "match_offer"
    __table_args__ = (
        Index(
            "uq_match_offer_pending",
            "request_id",
            "team_id",
            unique=True,
            sqlite_where=text("status = 'PENDING'"),
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("match_request.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    version: Mapped[int] = mapped_column(default=1)
    proposed_start: Mapped[datetime] = mapped_column(UtcDateTime)
    referee_mode: Mapped[str] = mapped_column(String(20))
    place_kind: Mapped[str] = mapped_column(String(20))
    place_note: Mapped[str | None] = mapped_column(String(120), nullable=True)
    message: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
'@
Write-RivalText 'backend\app\persistence\models_places.py' @'
"""Catálogo de barrios con su punto central (ADR-006). No hay coordenadas de personas ni de equipos."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class Neighborhood(Base):
    __tablename__ = "neighborhood"
    __table_args__ = (UniqueConstraint("city_key", "name_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    name_key: Mapped[str] = mapped_column(String(60))
    city: Mapped[str] = mapped_column(String(60))
    city_key: Mapped[str] = mapped_column(String(60), index=True)
    center_lat: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    center_lon: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    source: Mapped[str] = mapped_column(String(120))
    imported_at: Mapped[datetime] = mapped_column(UtcDateTime)
'@
Write-RivalText 'backend\app\persistence\models_scouting.py' @'
"""Perfil de agente libre: un jugador sin equipo que quiere ser encontrado para un deporte."""

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class FreeAgentProfile(Base):
    __tablename__ = "free_agent_profile"
    __table_args__ = (UniqueConstraint("user_id", "sport_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"), index=True)
    sport_code: Mapped[str] = mapped_column(String(30), index=True)
    position: Mapped[str | None] = mapped_column(String(40), nullable=True)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)
'@
Write-RivalText 'backend\app\persistence\models_teams.py' @'
"""Tablas de equipos, membresías y solicitudes de unión."""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.database import Base, UtcDateTime


class Team(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    name_key: Mapped[str] = mapped_column(String(60), index=True)
    sport_code: Mapped[str] = mapped_column(String(30), index=True)
    modality_code: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(60))
    city_key: Mapped[str] = mapped_column(String(60), index=True)
    neighborhood: Mapped[str] = mapped_column(String(60))
    neighborhood_key: Mapped[str] = mapped_column(String(60), index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)

    memberships: Mapped[list["TeamMembership"]] = relationship(
        back_populates="team", cascade="all, delete-orphan", lazy="selectin", order_by="TeamMembership.id"
    )


def _one_per_team(name: str, role: str) -> Index:
    """Índice único parcial: como máximo un DT y un capitán por equipo, garantizado por la base."""
    condition = text(f"role = '{role}'")
    return Index(name, "team_id", unique=True, sqlite_where=condition, postgresql_where=condition)


class TeamMembership(Base):
    __tablename__ = "team_membership"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id"),
        _one_per_team("uq_team_one_coach", "COACH"),
        _one_per_team("uq_team_one_captain", "CAPTAIN"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    joined_at: Mapped[datetime] = mapped_column(UtcDateTime)

    team: Mapped[Team] = relationship(back_populates="memberships")


class JoinRequest(Base):
    __tablename__ = "join_request"
    __table_args__ = (
        Index(
            "uq_join_request_pending",
            "team_id",
            "user_id",
            unique=True,
            sqlite_where=text("status = 'PENDING'"),
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    desired_role: Mapped[str] = mapped_column(String(20))
    # REQUEST: el jugador pide entrar. INVITE: el equipo invita a un agente libre.
    direction: Mapped[str] = mapped_column(String(10), default="REQUEST")
    initiated_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    message: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
'@
Write-RivalText 'backend\app\services\__init__.py' @'

'@
Write-RivalText 'backend\app\services\audit_service.py' @'
"""Registro de eventos de auditoría con hash SHA-256 encadenado.

Cada evento guarda el hash del anterior; alterar uno rompe la cadena y `verify_chain`
lo detecta. Es resistente a manipulación, no inmutable: un administrador con acceso
directo a la base podría reescribir toda la cadena (riesgo documentado).
"""

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models_audit import AuditEvent, AuditHead
from app.services.context import ServiceContext
from app.services.request_context import current_correlation_id

SOFTWARE_VERSION = "0.1.0"
GENESIS_HASH = "0" * 64


def _to_json(data: Mapping[str, Any] | None) -> str | None:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)


def _compute_hash(event: AuditEvent) -> str:
    payload = "|".join(
        [
            str(event.chain_position),
            event.software_version,
            event.prev_hash,
            event.occurred_at.isoformat(),
            event.actor_type,
            str(event.initiated_by),
            str(event.approved_by),
            event.action,
            event.entity,
            event.entity_id,
            event.before_json or "",
            event.after_json or "",
            event.correlation_id,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_event(
    ctx: ServiceContext,
    *,
    action: str,
    entity: str,
    entity_id: int | str,
    initiated_by: int | None,
    approved_by: int | None = None,
    actor_type: str = "HUMAN",
    before: Mapping[str, Any] | None = None,
    after: Mapping[str, Any] | None = None,
) -> AuditEvent:
    # Bloquea el eslabón final: dos peticiones simultáneas escriben una después de la otra.
    head = ctx.db.get(AuditHead, 1, with_for_update=True)
    if head is None:
        raise RuntimeError("Falta la fila audit_head; ejecuta create_schema")
    event = AuditEvent(
        chain_position=head.last_position + 1,
        occurred_at=ctx.clock.now(),
        actor_type=actor_type,
        initiated_by=initiated_by,
        approved_by=approved_by,
        action=action,
        entity=entity,
        entity_id=str(entity_id),
        before_json=_to_json(before),
        after_json=_to_json(after),
        correlation_id=current_correlation_id(),
        software_version=SOFTWARE_VERSION,
        prev_hash=head.last_hash,
    )
    event.integrity_hash = _compute_hash(event)
    ctx.db.add(event)
    head.last_hash = event.integrity_hash
    head.last_position = event.chain_position
    ctx.db.flush()
    return event


def verify_chain(db: Session) -> bool:
    """Recorre la cadena en orden y comprueba cada hash y que el final coincida con audit_head."""
    expected_prev = GENESIS_HASH
    expected_position = 0
    for event in db.scalars(select(AuditEvent).order_by(AuditEvent.chain_position)):
        expected_position += 1
        if (
            event.chain_position != expected_position
            or event.prev_hash != expected_prev
            or _compute_hash(event) != event.integrity_hash
        ):
            return False
        expected_prev = event.integrity_hash
    head = db.get(AuditHead, 1)
    return head is not None and head.last_hash == expected_prev and head.last_position == expected_position
'@
Write-RivalText 'backend\app\services\auth_service.py' @'
"""Casos de uso de identidad: registro por rol, inicio y cierre de sesión, agregar rol."""

import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.age_policy import is_adult
from app.domain.errors import AuthenticationError, ConflictError, DomainError
from app.domain.identity_rules import (
    normalize_email,
    validate_display_name,
    validate_password,
    validate_place_name,
)
from app.domain.roles import UserRole
from app.domain.text_keys import search_key
from app.persistence.models_identity import AuthSession, UserAccount, UserRoleRow, UserSport
from app.services.audit_service import record_event
from app.services.clock import local_today
from app.services.context import ServiceContext
from app.services.inputs import RegisterInput
from app.services.passwords import hash_password, verify_password
from app.services.rate_limiter import LoginRateLimiter

_INVALID_LOGIN = "Correo o contraseña incorrectos."
_INVALID_SESSION = "Tu sesión terminó. Inicia sesión de nuevo."


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _check_sports(ctx: ServiceContext, sports: list[str]) -> list[str]:
    unique = sorted(set(sports))
    if not unique:
        raise DomainError("SPORTS_REQUIRED", "Elige al menos un deporte.")
    for code in unique:
        if not ctx.catalog.has_sport(code):
            raise DomainError("UNKNOWN_SPORT", f"El deporte {code} no está en el catálogo.")
    return unique


def register_user(ctx: ServiceContext, data: RegisterInput) -> UserAccount:
    email = normalize_email(data.email)
    validate_password(data.password)
    if not is_adult(data.birth_date, local_today(ctx.clock)):
        raise DomainError("UNDERAGE", "Por ahora RIVAL es solo para mayores de 18 años.")
    sports = _check_sports(ctx, data.sports)
    if ctx.db.scalar(select(UserAccount.id).where(UserAccount.email == email)):
        raise ConflictError("EMAIL_TAKEN", "Ya existe una cuenta con ese correo.")
    now = ctx.clock.now()
    city = validate_place_name(data.city, "ciudad")
    neighborhood = validate_place_name(data.neighborhood, "barrio")
    user = UserAccount(
        email=email,
        password_hash=hash_password(data.password),
        display_name=validate_display_name(data.display_name),
        birth_date=data.birth_date,
        city=city,
        city_key=search_key(city),
        neighborhood=neighborhood,
        neighborhood_key=search_key(neighborhood),
        position=(data.position or "").strip()[:40] or None,
        created_at=now,
        roles=[UserRoleRow(role=data.role.value, created_at=now)],
        sports=[UserSport(sport_code=code) for code in sports],
    )
    ctx.db.add(user)
    try:
        ctx.db.flush()
    except IntegrityError as error:  # dos registros simultáneos con el mismo correo
        raise ConflictError("EMAIL_TAKEN", "Ya existe una cuenta con ese correo.") from error
    record_event(
        ctx,
        action="USER_REGISTERED",
        entity="user_account",
        entity_id=user.id,
        initiated_by=user.id,
        after={"display_name": user.display_name, "role": data.role.value, "sports": sports},
    )
    return user


def login(
    ctx: ServiceContext, limiter: LoginRateLimiter, email: str, password: str, client_key: str
) -> tuple[str, UserAccount]:
    key = f"{email.strip().lower()}|{client_key}"
    now = ctx.clock.now()
    limiter.check(key, now)
    user = ctx.db.scalar(select(UserAccount).where(UserAccount.email == email.strip().lower()))
    if not verify_password(user.password_hash if user else None, password) or user is None:
        limiter.register_failure(key, now)
        raise AuthenticationError("INVALID_CREDENTIALS", _INVALID_LOGIN)
    limiter.register_success(key)
    token = secrets.token_urlsafe(32)
    ctx.db.add(
        AuthSession(
            user_id=user.id,
            token_hash=_hash_token(token),
            created_at=now,
            last_seen_at=now,
            expires_at=now + ctx.session_ttl,
        )
    )
    record_event(ctx, action="USER_LOGGED_IN", entity="user_account", entity_id=user.id, initiated_by=user.id)
    return token, user


def authenticate(ctx: ServiceContext, token: str) -> UserAccount:
    session = ctx.db.scalar(select(AuthSession).where(AuthSession.token_hash == _hash_token(token)))
    now = ctx.clock.now()
    if session is None or session.expires_at <= now or now - session.last_seen_at > ctx.session_idle:
        if session is not None:
            ctx.db.delete(session)
            ctx.db.flush()
        raise AuthenticationError("SESSION_EXPIRED", _INVALID_SESSION)
    session.last_seen_at = now
    user = ctx.db.get(UserAccount, session.user_id)
    if user is None:
        raise AuthenticationError("SESSION_EXPIRED", _INVALID_SESSION)
    return user


def logout(ctx: ServiceContext, token: str) -> None:
    session = ctx.db.scalar(select(AuthSession).where(AuthSession.token_hash == _hash_token(token)))
    if session is not None:
        record_event(
            ctx, action="USER_LOGGED_OUT", entity="user_account", entity_id=session.user_id,
            initiated_by=session.user_id,
        )
        ctx.db.delete(session)
        ctx.db.flush()


def add_role(ctx: ServiceContext, user: UserAccount, role: UserRole, sports: list[str]) -> UserAccount:
    codes = _check_sports(ctx, sports)
    before = {"roles": sorted(r.role for r in user.roles)}
    if role.value not in before["roles"]:
        user.roles.append(UserRoleRow(role=role.value, created_at=ctx.clock.now()))
    known = {s.sport_code for s in user.sports}
    user.sports.extend(UserSport(sport_code=c) for c in codes if c not in known)
    ctx.db.flush()
    record_event(
        ctx, action="USER_ROLE_ADDED", entity="user_account", entity_id=user.id, initiated_by=user.id,
        before=before, after={"roles": sorted(r.role for r in user.roles)},
    )
    return user
'@
Write-RivalText 'backend\app\services\clock.py' @'
"""Reloj inyectable: el sistema real usa UTC; las pruebas usan un reloj fijo."""

from datetime import UTC, date, datetime, timedelta, timezone
from typing import Protocol

# Colombia no usa horario de verano; un desfase fijo evita depender de tzdata en Windows.
COLOMBIA_TZ = timezone(timedelta(hours=-5), name="America/Bogota")


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class FixedClock:
    def __init__(self, start: datetime) -> None:
        self._now = start

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now = self._now + delta


def local_today(clock: Clock) -> date:
    """Fecha calendario en Colombia, usada para calcular la edad."""
    return clock.now().astimezone(COLOMBIA_TZ).date()
'@
Write-RivalText 'backend\app\services\context.py' @'
"""Dependencias que comparten los casos de uso de una petición."""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.orm import Session

from app.domain.sports_catalog import SportCatalog
from app.services.clock import Clock


@dataclass
class ServiceContext:
    db: Session
    clock: Clock
    catalog: SportCatalog
    session_ttl: timedelta
    session_idle: timedelta
'@
Write-RivalText 'backend\app\services\free_agent_service.py' @'
"""Agentes libres: jugadores sin equipo que quieren ser encontrados, por deporte, barrio y ciudad."""

from dataclasses import dataclass

from sqlalchemy import func, select

from app.domain.errors import DomainError, PermissionDeniedError
from app.domain.roles import ROLES_THAT_CAN_CREATE_TEAMS, UserRole
from app.domain.text_keys import search_key
from app.persistence.models_identity import UserAccount
from app.persistence.models_scouting import FreeAgentProfile
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.team_service import MAX_PAGE_SIZE


@dataclass(frozen=True)
class FreeAgentView:
    user_id: int
    display_name: str
    sport_code: str
    position: str | None
    note: str | None
    neighborhood: str
    city: str


@dataclass(frozen=True)
class FreeAgentPage:
    items: list[FreeAgentView]
    page: int
    page_size: int
    total: int


def set_free_agent(
    ctx: ServiceContext, actor: UserAccount, sport_code: str, active: bool, position: str | None, note: str | None
) -> FreeAgentProfile:
    if not {UserRole(r.role) for r in actor.roles} & ROLES_THAT_CAN_CREATE_TEAMS:
        raise PermissionDeniedError("ROLE_CANNOT_BE_FREE_AGENT", "Agrega el rol de jugador para aparecer como agente libre.")
    if not ctx.catalog.has_sport(sport_code):
        raise DomainError("UNKNOWN_SPORT", f"El deporte {sport_code} no está en el catálogo.")
    profile = ctx.db.scalar(select(FreeAgentProfile).where(
        FreeAgentProfile.user_id == actor.id, FreeAgentProfile.sport_code == sport_code))
    before = {"active": profile.active} if profile else None
    if profile is None:
        profile = FreeAgentProfile(user_id=actor.id, sport_code=sport_code)
        ctx.db.add(profile)
    profile.active = active
    profile.position = (position or "").strip()[:40] or None
    profile.note = (note or "").strip()[:200] or None
    profile.updated_at = ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="FREE_AGENT_UPDATED", entity="free_agent_profile", entity_id=profile.id,
                 initiated_by=actor.id, before=before, after={"active": active, "sport": sport_code})
    return profile


def search(
    ctx: ServiceContext,
    actor: UserAccount,
    sport_code: str,
    city: str,
    neighborhood: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> FreeAgentPage:
    page, page_size = max(1, page), max(1, min(page_size, MAX_PAGE_SIZE))
    stmt = (
        select(FreeAgentProfile, UserAccount)
        .join(UserAccount, UserAccount.id == FreeAgentProfile.user_id)
        .where(FreeAgentProfile.active.is_(True), FreeAgentProfile.sport_code == sport_code,
               UserAccount.city_key == search_key(city))
    )
    if neighborhood:
        stmt = stmt.where(UserAccount.neighborhood_key == search_key(neighborhood))
    total = ctx.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = ctx.db.execute(
        stmt.order_by(FreeAgentProfile.updated_at.desc(), FreeAgentProfile.id).offset((page - 1) * page_size).limit(page_size)
    ).all()
    items = [
        FreeAgentView(user_id=u.id, display_name=u.display_name, sport_code=p.sport_code,
                      position=p.position or u.position, note=p.note, neighborhood=u.neighborhood, city=u.city)
        for p, u in rows
    ]
    return FreeAgentPage(items=items, page=page, page_size=page_size, total=total)


def deactivate(ctx: ServiceContext, user_id: int, sport_code: str) -> None:
    profile = ctx.db.scalar(select(FreeAgentProfile).where(
        FreeAgentProfile.user_id == user_id, FreeAgentProfile.sport_code == sport_code))
    if profile is not None and profile.active:
        profile.active = False
        profile.updated_at = ctx.clock.now()


def my_profiles(ctx: ServiceContext, actor: UserAccount) -> list[FreeAgentProfile]:
    return list(ctx.db.scalars(select(FreeAgentProfile).where(FreeAgentProfile.user_id == actor.id)
                               .order_by(FreeAgentProfile.sport_code)))
'@
Write-RivalText 'backend\app\services\inputs.py' @'
"""Datos de entrada de los casos de uso (ya validados en forma por la API)."""

from dataclasses import dataclass, field
from datetime import date

from app.domain.roles import TeamRole, UserRole


@dataclass
class RegisterInput:
    email: str
    password: str
    display_name: str
    birth_date: date
    role: UserRole
    sports: list[str]
    city: str
    neighborhood: str
    position: str | None = None


@dataclass
class CreateTeamInput:
    name: str
    sport_code: str
    modality_code: str
    city: str
    neighborhood: str
    as_coach: bool = False


@dataclass
class JoinRequestInput:
    desired_role: TeamRole = TeamRole.PLAYER
    message: str | None = None


@dataclass
class TeamSearchInput:
    sport_code: str | None = None
    modality_code: str | None = None
    city: str | None = None
    query: str | None = None
    page: int = 1
    page_size: int = field(default=20)
'@
Write-RivalText 'backend\app\services\invitation_service.py' @'
"""Invitaciones de un equipo a un agente libre. El jugador siempre decide si entra."""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.domain.errors import ConflictError, NotFoundError
from app.domain.roles import TeamRole
from app.persistence.models_identity import UserAccount
from app.persistence.models_scouting import FreeAgentProfile
from app.persistence.models_teams import JoinRequest, Team, TeamMembership
from app.services import free_agent_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.team_service import get_active_team, require_admin, summary
from app.services.team_views import TeamSummaryView

_PENDING = "PENDING"
MAX_PENDING_INVITATIONS = 20
REINVITE_COOLDOWN = timedelta(days=7)
_ALREADY = "Ya hay una invitación o solicitud pendiente entre este equipo y esa persona."


@dataclass(frozen=True)
class InvitationView:
    id: int
    team: TeamSummaryView
    message: str | None


def invite(ctx: ServiceContext, actor: UserAccount, team_id: int, user_id: int, message: str | None) -> JoinRequest:
    team = get_active_team(ctx, team_id)
    require_admin(team, actor)
    if any(m.user_id == user_id for m in team.memberships):
        raise ConflictError("ALREADY_MEMBER", "Esa persona ya está en tu equipo.")
    free_agent = ctx.db.scalar(select(FreeAgentProfile.id).where(
        FreeAgentProfile.user_id == user_id, FreeAgentProfile.sport_code == team.sport_code,
        FreeAgentProfile.active.is_(True)))
    if free_agent is None:
        raise ConflictError("NOT_A_FREE_AGENT", "Solo puedes invitar a agentes libres de este deporte.")
    pending = ctx.db.scalar(select(JoinRequest.id).where(
        JoinRequest.team_id == team.id, JoinRequest.user_id == user_id, JoinRequest.status == _PENDING))
    if pending:
        raise ConflictError("INVITATION_ALREADY_PENDING", _ALREADY)
    _check_invitation_limits(ctx, team.id, user_id)
    invitation = JoinRequest(
        team_id=team.id, user_id=user_id, desired_role=TeamRole.PLAYER.value, direction="INVITE",
        initiated_by=actor.id, message=(message or "").strip()[:200] or None, status=_PENDING,
        created_at=ctx.clock.now(),
    )
    ctx.db.add(invitation)
    try:
        ctx.db.flush()
    except IntegrityError as error:
        raise ConflictError("INVITATION_ALREADY_PENDING", _ALREADY) from error
    record_event(ctx, action="PLAYER_INVITED", entity="join_request", entity_id=invitation.id,
                 initiated_by=actor.id, after={"team_id": team.id, "user_id": user_id})
    return invitation


def _check_invitation_limits(ctx: ServiceContext, team_id: int, user_id: int) -> None:
    """Evita el acoso: tope de invitaciones pendientes y una semana de espera tras un rechazo."""
    open_count = ctx.db.scalar(select(func.count()).select_from(JoinRequest).where(
        JoinRequest.team_id == team_id, JoinRequest.direction == "INVITE", JoinRequest.status == _PENDING)) or 0
    if open_count >= MAX_PENDING_INVITATIONS:
        raise ConflictError("TOO_MANY_INVITATIONS", "Tu equipo tiene 20 invitaciones sin responder. Espera respuestas.")
    recent_rejection = ctx.db.scalar(select(JoinRequest.id).where(
        JoinRequest.team_id == team_id, JoinRequest.user_id == user_id, JoinRequest.direction == "INVITE",
        JoinRequest.status == "REJECTED", JoinRequest.decided_at > ctx.clock.now() - REINVITE_COOLDOWN))
    if recent_rejection:
        raise ConflictError("INVITATION_COOLDOWN", "Esta persona rechazó tu invitación hace poco. Espera 7 días.")


def my_invitations(ctx: ServiceContext, actor: UserAccount) -> list[InvitationView]:
    rows = ctx.db.execute(
        select(JoinRequest, Team).join(Team, Team.id == JoinRequest.team_id).where(
            JoinRequest.user_id == actor.id, JoinRequest.direction == "INVITE",
            JoinRequest.status == _PENDING, Team.status == "ACTIVE").order_by(JoinRequest.id)
    ).all()
    return [InvitationView(id=r.id, team=summary(t), message=r.message) for r, t in rows]


def respond(ctx: ServiceContext, actor: UserAccount, invitation_id: int, accept: bool) -> JoinRequest:
    invitation = ctx.db.get(JoinRequest, invitation_id)
    # A quien no es el invitado se le responde igual que si no existiera.
    if invitation is None or invitation.direction != "INVITE" or invitation.user_id != actor.id:
        raise NotFoundError("INVITATION_NOT_FOUND", "La invitación no existe.")
    team = get_active_team(ctx, invitation.team_id, lock=True)
    ctx.db.refresh(invitation)  # un doble toque pudo responderla mientras esperábamos el bloqueo
    if invitation.status != _PENDING:
        raise ConflictError("INVITATION_ALREADY_DECIDED", "Esta invitación ya fue respondida.")
    now = ctx.clock.now()
    invitation.status = "APPROVED" if accept else "REJECTED"
    invitation.decided_by, invitation.decided_at = actor.id, now
    if accept:
        team.memberships.append(TeamMembership(user_id=actor.id, role=TeamRole.PLAYER.value, joined_at=now))
        free_agent_service.deactivate(ctx, actor.id, team.sport_code)
    ctx.db.flush()
    record_event(ctx, action="INVITATION_ACCEPTED" if accept else "INVITATION_REJECTED", entity="join_request",
                 entity_id=invitation.id, initiated_by=invitation.initiated_by, approved_by=actor.id,
                 before={"status": _PENDING}, after={"status": invitation.status})
    return invitation
'@
Write-RivalText 'backend\app\services\ip_limiter.py' @'
"""Límite por equipo cliente (IP) con ventana deslizante, para registro e inicio de sesión.

Complementa al límite por correo: impide probar muchos correos distintos desde el mismo
lugar (enumeración de cuentas y consumo de CPU por Argon2). En memoria y con purga
periódica; con varios procesos se moverá a Redis (ADR-003).

[POR VERIFICAR] Detrás de un proxy, la IP debe venir de un encabezado de confianza
configurable; hoy se usa la IP de la conexión.
"""

from collections import deque
from datetime import datetime, timedelta
from threading import Lock

from app.domain.errors import RateLimitedError

MAX_TRACKED_KEYS = 10_000


class SlidingWindowLimiter:
    def __init__(self, max_events: int, window: timedelta) -> None:
        self._max_events = max_events
        self._window = window
        self._events: dict[str, deque[datetime]] = {}
        self._lock = Lock()

    def hit(self, key: str, now: datetime) -> None:
        """Cuenta un intento; si ya se superó el máximo en la ventana, lo rechaza."""
        with self._lock:
            if len(self._events) > MAX_TRACKED_KEYS:
                self._purge(now)
            events = self._events.setdefault(key, deque())
            while events and now - events[0] >= self._window:
                events.popleft()
            if len(events) >= self._max_events:
                wait = int((events[0] + self._window - now).total_seconds()) + 1
                raise RateLimitedError(
                    "TOO_MANY_REQUESTS",
                    f"Demasiados intentos desde este equipo. Espera {wait} segundos.",
                    retry_after_seconds=wait,
                )
            events.append(now)

    def _purge(self, now: datetime) -> None:
        stale = [k for k, v in self._events.items() if not v or now - v[-1] >= self._window]
        for key in stale:
            del self._events[key]


def register_limiter() -> SlidingWindowLimiter:
    return SlidingWindowLimiter(max_events=10, window=timedelta(hours=1))


def login_ip_limiter() -> SlidingWindowLimiter:
    return SlidingWindowLimiter(max_events=30, window=timedelta(minutes=15))


def search_limiter() -> SlidingWindowLimiter:
    """Búsquedas de rivales, partidos y agentes libres por usuario."""
    return SlidingWindowLimiter(max_events=60, window=timedelta(minutes=10))
'@
Write-RivalText 'backend\app\services\join_service.py' @'
"""Solicitudes para unirse a un equipo: pedir, listar (administrador) y decidir."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.roles import TeamRole, UserRole
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import JoinRequest, TeamMembership
from app.services import free_agent_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.inputs import JoinRequestInput
from app.domain.team_rules import resolve_admin
from app.services.team_service import get_active_team, member_views, record_admin_change, require_admin
from app.services.team_views import JoinRequestView

_PENDING = "PENDING"


def request_join(ctx: ServiceContext, actor: UserAccount, team_id: int, data: JoinRequestInput) -> JoinRequest:
    team = get_active_team(ctx, team_id)
    if any(m.user_id == actor.id for m in team.memberships):
        raise ConflictError("ALREADY_MEMBER", "Ya eres parte de este equipo.")
    account_roles = {r.role for r in actor.roles}
    if not account_roles & {UserRole.PLAYER.value, UserRole.COACH.value}:
        raise PermissionDeniedError(
            "ROLE_CANNOT_JOIN_TEAM", "Agrega el rol de jugador o DT a tu cuenta para unirte a un equipo."
        )
    if data.desired_role == TeamRole.CAPTAIN:
        raise PermissionDeniedError("INVALID_DESIRED_ROLE", "El capitán lo nombra el administrador del equipo.")
    if data.desired_role == TeamRole.COACH and UserRole.COACH.value not in account_roles:
        raise PermissionDeniedError("COACH_ROLE_REQUIRED", "Para entrar como DT agrega el rol de director técnico.")
    existing = ctx.db.scalar(select(JoinRequest.id).where(
        JoinRequest.team_id == team.id, JoinRequest.user_id == actor.id, JoinRequest.status == _PENDING))
    if existing:
        raise ConflictError("REQUEST_ALREADY_PENDING", "Ya enviaste una solicitud; espera la respuesta del equipo.")
    request = JoinRequest(
        team_id=team.id, user_id=actor.id, desired_role=data.desired_role.value, initiated_by=actor.id,
        message=(data.message or "").strip()[:200] or None, status=_PENDING, created_at=ctx.clock.now(),
    )
    ctx.db.add(request)
    try:
        ctx.db.flush()
    except IntegrityError as error:
        raise ConflictError("REQUEST_ALREADY_PENDING", "Ya enviaste una solicitud; espera la respuesta del equipo.") from error
    record_event(ctx, action="JOIN_REQUESTED", entity="join_request", entity_id=request.id,
                 initiated_by=actor.id, after={"team_id": team.id, "desired_role": request.desired_role})
    return request


def list_requests(ctx: ServiceContext, actor: UserAccount, team_id: int) -> list[JoinRequestView]:
    team = get_active_team(ctx, team_id)
    require_admin(team, actor)
    rows = ctx.db.execute(
        select(JoinRequest, UserAccount).join(UserAccount, UserAccount.id == JoinRequest.user_id)
        .where(JoinRequest.team_id == team.id, JoinRequest.status == _PENDING, JoinRequest.direction == "REQUEST")
        .order_by(JoinRequest.id)
    ).all()
    return [
        JoinRequestView(id=r.id, team_id=r.team_id, user_id=r.user_id, display_name=u.display_name,
                        position=u.position, desired_role=TeamRole(r.desired_role), message=r.message,
                        status=r.status)
        for r, u in rows
    ]


def decide(ctx: ServiceContext, actor: UserAccount, request_id: int, approve: bool) -> JoinRequest:
    request = ctx.db.get(JoinRequest, request_id)
    if request is None or request.direction != "REQUEST":
        raise NotFoundError("REQUEST_NOT_FOUND", "La solicitud no existe.")
    team = get_active_team(ctx, request.team_id, lock=True)
    require_admin(team, actor)
    ctx.db.refresh(request)  # otra petición pudo decidirla mientras esperábamos el bloqueo
    if request.status != _PENDING:
        raise ConflictError("REQUEST_ALREADY_DECIDED", "Esta solicitud ya fue respondida.")
    if approve and request.desired_role == TeamRole.COACH and any(m.role == TeamRole.COACH for m in team.memberships):
        raise ConflictError("TEAM_HAS_COACH", "El equipo ya tiene DT. Acepta a la persona como jugador o rechaza.")
    admin_before = resolve_admin(member_views(team))
    now = ctx.clock.now()
    request.status = "APPROVED" if approve else "REJECTED"
    request.decided_by = actor.id
    request.decided_at = now
    if approve:
        team.memberships.append(TeamMembership(user_id=request.user_id, role=request.desired_role, joined_at=now))
        free_agent_service.deactivate(ctx, request.user_id, team.sport_code)
    ctx.db.flush()
    record_event(ctx, action="JOIN_APPROVED" if approve else "JOIN_REJECTED", entity="join_request",
                 entity_id=request.id, initiated_by=request.user_id, approved_by=actor.id,
                 before={"status": _PENDING}, after={"status": request.status, "role": request.desired_role})
    record_admin_change(ctx, team, admin_before, actor.id)
    return request
'@
Write-RivalText 'backend\app\services\match_feed_service.py' @'
"""Búsquedas de partido abiertas que un equipo puede responder.

Una solicitud se ve solo si el equipo que mira está dentro del alcance que pidió quien
la publicó (cercanía, barrio o ciudad) y dentro del alcance que eligió quien mira.
Los retos directos solo los ve el equipo retado. La misma regla protege las ofertas.
"""

from sqlalchemy import and_, func, or_, select

from app.domain.geo import DEFAULT_RADIUS_KM, MAX_RADIUS_KM, SearchScope, distance_band
from app.domain.match_rules import OfferStatus, RequestStatus
from app.persistence.models_identity import UserAccount
from app.persistence.models_matches import MatchOffer, MatchRequest
from app.persistence.models_teams import Team
from app.services import neighborhood_service
from app.services.context import ServiceContext
from app.services.match_request_service import to_view
from app.services.match_views import MatchRequestView
from app.services.rival_service import require_member
from app.services.team_service import get_active_team

MAX_RESULTS = 200


def _in_scope(scope: str, radius_km: int | None, same_barrio: bool, km: float | None) -> bool:
    if scope == SearchScope.CITY:
        return True
    if scope == SearchScope.NEIGHBORHOOD:
        return same_barrio
    return km is not None and km <= (radius_km or DEFAULT_RADIUS_KM)


def viewer_distances(ctx: ServiceContext, viewer: Team) -> dict[str, float]:
    """Distancia desde el barrio de quien mira a cada barrio de su ciudad dentro del radio máximo."""
    return neighborhood_service.neighborhoods_within(ctx, viewer.city, viewer.neighborhood, radius_km=MAX_RADIUS_KM)


def is_visible_to(request: MatchRequest, owner: Team, viewer: Team, distances: dict[str, float]) -> bool:
    """¿Puede `viewer` ver (y por tanto ofertar a) esta búsqueda?"""
    if owner.id == viewer.id or (request.sport_code, request.modality_code) != (viewer.sport_code, viewer.modality_code):
        return False
    if request.target_team_id is not None:
        return request.target_team_id == viewer.id
    if owner.city_key != viewer.city_key:
        return False
    same_barrio = owner.neighborhood_key == viewer.neighborhood_key
    return _in_scope(request.scope, request.radius_km, same_barrio, distances.get(owner.neighborhood_key))


def open_requests_for(
    ctx: ServiceContext, actor: UserAccount, team_id: int, scope: SearchScope, radius_km: int = DEFAULT_RADIUS_KM
) -> list[MatchRequestView]:
    viewer = get_active_team(ctx, team_id)
    require_member(viewer, actor)
    distances = viewer_distances(ctx, viewer)
    reachable = list(distances) or [viewer.neighborhood_key]
    rows = ctx.db.execute(
        select(MatchRequest, Team).join(Team, Team.id == MatchRequest.team_id).where(
            MatchRequest.status == RequestStatus.OPEN, MatchRequest.window_end > ctx.clock.now(),
            MatchRequest.team_id != viewer.id, MatchRequest.sport_code == viewer.sport_code,
            MatchRequest.modality_code == viewer.modality_code, Team.status == "ACTIVE",
            or_(
                MatchRequest.target_team_id == viewer.id,
                and_(MatchRequest.target_team_id.is_(None), Team.city_key == viewer.city_key,
                     or_(MatchRequest.scope == SearchScope.CITY.value, Team.neighborhood_key.in_(reachable))),
            ),
        ).order_by(MatchRequest.window_start, MatchRequest.id).limit(MAX_RESULTS * 2)
    ).all()
    visible = []
    for request, owner in rows:
        km = distances.get(owner.neighborhood_key)
        same_barrio = owner.neighborhood_key == viewer.neighborhood_key
        direct = request.target_team_id == viewer.id
        if is_visible_to(request, owner, viewer, distances) and (direct or _in_scope(scope, radius_km, same_barrio, km)):
            visible.append((request, km))
    visible = visible[:MAX_RESULTS]
    pending = dict(ctx.db.execute(
        select(MatchOffer.request_id, func.count()).where(
            MatchOffer.request_id.in_([r.id for r, _ in visible]), MatchOffer.status == OfferStatus.PENDING)
        .group_by(MatchOffer.request_id)).tuples().all())
    return [to_view(ctx, r, distance_band(km) if km is not None else None, pending.get(r.id, 0)) for r, km in visible]
'@
Write-RivalText 'backend\app\services\match_offer_service.py' @'
"""Ofertas de rivales a una búsqueda de partido, al estilo InDriver.

Una contraoferta del mismo equipo crea una versión nueva y deja la anterior SUPERSEDED.
Aceptar bloquea la solicitud (FOR UPDATE): dos aceptaciones simultáneas no pueden ganar ambas.
"""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.domain.errors import ConflictError, NotFoundError
from app.domain.match_rules import (
    OfferStatus,
    RefereeMode,
    RequestStatus,
    check_offer_referee,
    check_proposed_start,
)
from app.persistence.models_identity import UserAccount
from app.persistence.models_matches import MatchOffer, MatchRequest
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.match_feed_service import is_visible_to, viewer_distances
from app.services.match_request_service import effective_status, get_request
from app.services.match_views import OfferInput, OfferView
from app.services.team_service import get_active_team, require_admin, resolve_admin_id, summary

_PENDING = OfferStatus.PENDING.value


def _require_open(ctx: ServiceContext, request: MatchRequest) -> None:
    if effective_status(request, ctx) != RequestStatus.OPEN:
        raise ConflictError("MATCH_REQUEST_CLOSED", "Esta búsqueda ya está cerrada o venció.")


def make_offer(ctx: ServiceContext, actor: UserAccount, team_id: int, request_id: int, data: OfferInput) -> MatchOffer:
    team = get_active_team(ctx, team_id)
    require_admin(team, actor)
    request = get_request(ctx, request_id, lock=True)
    _require_open(ctx, request)
    if request.team_id == team.id:
        raise ConflictError("OWN_REQUEST", "No puedes ofertar a la búsqueda de tu propio equipo.")
    owner = ctx.db.get(Team, request.team_id)
    if owner is None or not is_visible_to(request, owner, team, viewer_distances(ctx, team)):
        raise NotFoundError("MATCH_REQUEST_NOT_FOUND", "La búsqueda de partido no existe.")
    check_proposed_start(data.proposed_start, request.window_start, request.window_end, ctx.clock.now())
    check_offer_referee(RefereeMode(request.referee_mode), data.referee_mode)
    previous = ctx.db.scalar(select(MatchOffer).where(
        MatchOffer.request_id == request.id, MatchOffer.team_id == team.id, MatchOffer.status == _PENDING))
    if previous is not None:
        previous.status = OfferStatus.SUPERSEDED.value
        ctx.db.flush()  # libera el índice único de oferta pendiente antes de crear la nueva versión
    offer = MatchOffer(
        request_id=request.id, team_id=team.id, version=_next_version(ctx, request.id, team.id),
        proposed_start=data.proposed_start, referee_mode=data.referee_mode.value, place_kind=data.place_kind.value,
        place_note=(data.place_note or "").strip()[:120] or None, message=(data.message or "").strip()[:200] or None,
        status=_PENDING, created_by=actor.id, created_at=ctx.clock.now(),
    )
    ctx.db.add(offer)
    try:
        ctx.db.flush()
    except IntegrityError as error:
        raise ConflictError("OFFER_ALREADY_PENDING", "Ya hay una oferta pendiente de tu equipo.") from error
    record_event(ctx, action="MATCH_OFFER_MADE", entity="match_offer", entity_id=offer.id, initiated_by=actor.id,
                 after={"request_id": request.id, "team_id": team.id, "version": offer.version,
                        "proposed_start": offer.proposed_start.isoformat()})
    return offer


def _next_version(ctx: ServiceContext, request_id: int, team_id: int) -> int:
    last = ctx.db.scalar(select(func.max(MatchOffer.version)).where(
        MatchOffer.request_id == request_id, MatchOffer.team_id == team_id))
    return (last or 0) + 1


def _get_offer(ctx: ServiceContext, offer_id: int) -> MatchOffer:
    offer = ctx.db.get(MatchOffer, offer_id)
    if offer is None:
        raise NotFoundError("OFFER_NOT_FOUND", "La oferta no existe.")
    return offer


def decide(ctx: ServiceContext, actor: UserAccount, offer_id: int, accept: bool) -> MatchOffer:
    """El administrador del equipo que publicó la búsqueda acepta o rechaza una oferta."""
    offer = _get_offer(ctx, offer_id)
    request = get_request(ctx, offer.request_id, lock=True)
    require_admin(get_active_team(ctx, request.team_id), actor)
    ctx.db.refresh(offer)
    _require_open(ctx, request)
    if offer.status != _PENDING:
        raise ConflictError("OFFER_NOT_PENDING", "Esta oferta ya no está pendiente.")
    now = ctx.clock.now()
    if accept and offer.proposed_start < now:
        raise ConflictError("OFFER_IN_PAST", "La hora de esta oferta ya pasó. Pide una oferta nueva.")
    offer.status = (OfferStatus.ACCEPTED if accept else OfferStatus.REJECTED).value
    offer.decided_by, offer.decided_at = actor.id, now
    if accept:
        request.status, request.accepted_offer_id, request.closed_at = RequestStatus.MATCHED.value, offer.id, now
        for other in ctx.db.scalars(select(MatchOffer).where(
                MatchOffer.request_id == request.id, MatchOffer.status == _PENDING, MatchOffer.id != offer.id)):
            other.status, other.decided_by, other.decided_at = OfferStatus.SUPERSEDED.value, actor.id, now
    ctx.db.flush()
    offering_admin = resolve_admin_id(ctx, offer.team_id)
    record_event(ctx, action="MATCH_OFFER_ACCEPTED" if accept else "MATCH_OFFER_REJECTED", entity="match_offer",
                 entity_id=offer.id, initiated_by=offering_admin, approved_by=actor.id,
                 before={"status": _PENDING}, after={"status": offer.status, "request_status": request.status})
    return offer


def withdraw(ctx: ServiceContext, actor: UserAccount, offer_id: int) -> MatchOffer:
    offer = _get_offer(ctx, offer_id)
    require_admin(get_active_team(ctx, offer.team_id), actor)
    get_request(ctx, offer.request_id, lock=True)  # mismo orden de bloqueo que aceptar: no pueden cruzarse
    ctx.db.refresh(offer)
    if offer.status != _PENDING:
        raise ConflictError("OFFER_NOT_PENDING", "Esta oferta ya no está pendiente.")
    offer.status, offer.decided_by, offer.decided_at = OfferStatus.WITHDRAWN.value, actor.id, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="MATCH_OFFER_WITHDRAWN", entity="match_offer", entity_id=offer.id,
                 initiated_by=actor.id, before={"status": _PENDING}, after={"status": offer.status})
    return offer


def list_offers(ctx: ServiceContext, actor: UserAccount, request_id: int) -> list[OfferView]:
    """Los miembros del equipo que publicó ven todas; cualquier otro ve solo las de sus equipos."""
    request = get_request(ctx, request_id)
    owner = get_active_team(ctx, request.team_id)
    stmt = select(MatchOffer, Team).join(Team, Team.id == MatchOffer.team_id).where(MatchOffer.request_id == request.id)
    if not any(m.user_id == actor.id for m in owner.memberships):
        mine = [t.id for t in ctx.db.scalars(select(Team).where(Team.memberships.any(user_id=actor.id)))]
        stmt = stmt.where(MatchOffer.team_id.in_(mine))
    rows = ctx.db.execute(stmt.order_by(MatchOffer.id)).all()
    return [
        OfferView(id=o.id, request_id=o.request_id, team=summary(t), version=o.version,
                  proposed_start=o.proposed_start, referee_mode=o.referee_mode, place_kind=o.place_kind,
                  place_note=o.place_note, message=o.message, status=o.status)
        for o, t in rows
    ]
'@
Write-RivalText 'backend\app\services\match_request_service.py' @'
"""Solicitudes de partido: abiertas (para equipos cercanos) o retos directos a un equipo."""

from sqlalchemy import func, select

from app.domain.errors import ConflictError, DomainError, NotFoundError
from app.domain.geo import DistanceBand, SearchScope, validate_radius_km
from app.domain.match_rules import MAX_OPEN_REQUESTS_PER_TEAM, OfferStatus, RequestStatus, validate_window
from app.persistence.models_identity import UserAccount
from app.persistence.models_matches import MatchOffer, MatchRequest
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.match_views import MatchRequestInput, MatchRequestView
from app.services.rival_service import nearby_keys, require_member
from app.services.team_service import get_active_team, require_admin, summary


def effective_status(request: MatchRequest, ctx: ServiceContext) -> str:
    if request.status == RequestStatus.OPEN and request.window_end <= ctx.clock.now():
        return "EXPIRED"
    return request.status


def to_view(
    ctx: ServiceContext, request: MatchRequest, band: DistanceBand | None = None, pending: int | None = None
) -> MatchRequestView:
    team = ctx.db.get(Team, request.team_id)
    assert team is not None
    if pending is None:
        pending = ctx.db.scalar(select(func.count()).select_from(MatchOffer).where(
            MatchOffer.request_id == request.id, MatchOffer.status == OfferStatus.PENDING)) or 0
    return MatchRequestView(
        id=request.id, team=summary(team), target_team_id=request.target_team_id, scope=request.scope,
        radius_km=request.radius_km, window_start=request.window_start, window_end=request.window_end,
        referee_mode=request.referee_mode, place_kind=request.place_kind, place_note=request.place_note,
        message=request.message, status=effective_status(request, ctx), distance_band=band,
        pending_offers=pending, accepted_offer_id=request.accepted_offer_id,
    )


def create_request(ctx: ServiceContext, actor: UserAccount, team_id: int, data: MatchRequestInput) -> MatchRequest:
    team = get_active_team(ctx, team_id, lock=True)
    require_admin(team, actor)
    now = ctx.clock.now()
    validate_window(data.window_start, data.window_end, now)
    open_count = ctx.db.scalar(select(func.count()).select_from(MatchRequest).where(
        MatchRequest.team_id == team.id, MatchRequest.status == RequestStatus.OPEN,
        MatchRequest.window_end > now)) or 0
    if open_count >= MAX_OPEN_REQUESTS_PER_TEAM:
        raise ConflictError("TOO_MANY_OPEN_REQUESTS", "Tu equipo ya tiene 3 búsquedas abiertas. Cierra una primero.")
    radius = None
    if data.scope == SearchScope.NEARBY:
        radius = validate_radius_km(data.radius_km or 0)
        nearby_keys(ctx, team, radius)  # falla con un mensaje claro si el barrio no está en el catálogo
    if data.target_team_id is not None:
        target = get_active_team(ctx, data.target_team_id)
        same_game = (target.sport_code, target.modality_code, target.city_key) == (
            team.sport_code, team.modality_code, team.city_key)
        if target.id == team.id or not same_game:
            raise DomainError("INVALID_CHALLENGE", "Solo puedes retar a otro equipo de tu ciudad, deporte y modalidad.")
    request = MatchRequest(
        team_id=team.id, target_team_id=data.target_team_id, sport_code=team.sport_code,
        modality_code=team.modality_code, scope=data.scope.value, radius_km=radius,
        window_start=data.window_start, window_end=data.window_end, referee_mode=data.referee_mode.value,
        place_kind=data.place_kind.value, place_note=(data.place_note or "").strip()[:120] or None,
        message=(data.message or "").strip()[:200] or None, status=RequestStatus.OPEN.value,
        created_by=actor.id, created_at=now,
    )
    ctx.db.add(request)
    ctx.db.flush()
    record_event(ctx, action="MATCH_REQUEST_CREATED", entity="match_request", entity_id=request.id,
                 initiated_by=actor.id, after={"team_id": team.id, "target_team_id": data.target_team_id,
                                               "scope": request.scope, "referee_mode": request.referee_mode})
    return request


def get_request(ctx: ServiceContext, request_id: int, lock: bool = False) -> MatchRequest:
    request = ctx.db.get(MatchRequest, request_id, with_for_update=lock)
    if request is None:
        raise NotFoundError("MATCH_REQUEST_NOT_FOUND", "La búsqueda de partido no existe.")
    return request


def cancel_request(ctx: ServiceContext, actor: UserAccount, request_id: int) -> MatchRequest:
    request = get_request(ctx, request_id, lock=True)
    require_admin(get_active_team(ctx, request.team_id), actor)
    if request.status != RequestStatus.OPEN:
        raise ConflictError("MATCH_REQUEST_CLOSED", "Esta búsqueda ya está cerrada.")
    now = ctx.clock.now()
    request.status, request.closed_at = RequestStatus.CANCELLED.value, now
    for offer in ctx.db.scalars(select(MatchOffer).where(
            MatchOffer.request_id == request.id, MatchOffer.status == OfferStatus.PENDING)):
        offer.status, offer.decided_by, offer.decided_at = OfferStatus.CANCELLED.value, actor.id, now
    ctx.db.flush()
    record_event(ctx, action="MATCH_REQUEST_CANCELLED", entity="match_request", entity_id=request.id,
                 initiated_by=actor.id, before={"status": "OPEN"}, after={"status": request.status})
    return request


def team_requests(ctx: ServiceContext, actor: UserAccount, team_id: int) -> list[MatchRequestView]:
    team = get_active_team(ctx, team_id)
    require_member(team, actor)
    rows = ctx.db.scalars(select(MatchRequest).where(MatchRequest.team_id == team.id)
                          .order_by(MatchRequest.id.desc()).limit(50))
    return [to_view(ctx, r) for r in rows]
'@
Write-RivalText 'backend\app\services\match_views.py' @'
"""Entradas y vistas de solicitudes de partido y ofertas."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.geo import DistanceBand, SearchScope
from app.domain.match_rules import PlaceKind, RefereeMode
from app.services.team_views import TeamSummaryView


@dataclass
class MatchRequestInput:
    window_start: datetime
    window_end: datetime
    scope: SearchScope
    referee_mode: RefereeMode
    place_kind: PlaceKind
    radius_km: int | None = None
    target_team_id: int | None = None
    place_note: str | None = None
    message: str | None = None


@dataclass
class OfferInput:
    proposed_start: datetime
    referee_mode: RefereeMode
    place_kind: PlaceKind
    place_note: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class MatchRequestView:
    id: int
    team: TeamSummaryView
    target_team_id: int | None
    scope: str
    radius_km: int | None
    window_start: datetime
    window_end: datetime
    referee_mode: str
    place_kind: str
    place_note: str | None
    message: str | None
    status: str
    distance_band: DistanceBand | None
    pending_offers: int
    accepted_offer_id: int | None


@dataclass(frozen=True)
class OfferView:
    id: int
    request_id: int
    team: TeamSummaryView
    version: int
    proposed_start: datetime
    referee_mode: str
    place_kind: str
    place_note: str | None
    message: str | None
    status: str
'@
Write-RivalText 'backend\app\services\membership_service.py' @'
"""Cambios de plantilla: nombrar capitán y salir del equipo.

Ambos bloquean la fila del equipo para que dos cambios simultáneos se apliquen en serie,
y la base de datos garantiza un solo DT y un solo capitán (índices únicos parciales).
"""

from app.domain.errors import ConflictError, NotFoundError
from app.domain.roles import TeamRole
from app.domain.team_rules import check_can_leave, resolve_admin
from app.persistence.models_identity import UserAccount
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.team_service import get_active_team, member_views, record_admin_change, require_admin


def set_captain(ctx: ServiceContext, actor: UserAccount, team_id: int, new_captain_id: int) -> None:
    """Si quien administra es el capitán y nombra a otro, la administración pasa al nuevo capitán."""
    team = get_active_team(ctx, team_id, lock=True)
    require_admin(team, actor)
    target = next((m for m in team.memberships if m.user_id == new_captain_id), None)
    if target is None:
        raise NotFoundError("MEMBER_NOT_FOUND", "Esa persona no está en la plantilla.")
    if target.role == TeamRole.COACH:
        raise ConflictError("COACH_CANNOT_BE_CAPTAIN", "El DT no puede ser también el capitán.")
    if target.role == TeamRole.CAPTAIN:
        return
    admin_before = resolve_admin(member_views(team))
    previous = next((m for m in team.memberships if m.role == TeamRole.CAPTAIN), None)
    if previous is not None:
        previous.role = TeamRole.PLAYER.value
        ctx.db.flush()  # primero se libera el puesto de capitán para no chocar con el índice único
    target.role = TeamRole.CAPTAIN.value
    ctx.db.flush()
    record_event(
        ctx, action="CAPTAIN_SET", entity="team", entity_id=team.id, initiated_by=actor.id,
        before={"captain": previous.user_id if previous else None},
        after={"captain": new_captain_id},
    )
    record_admin_change(ctx, team, admin_before, actor.id)


def leave_team(ctx: ServiceContext, actor: UserAccount, team_id: int) -> None:
    team = get_active_team(ctx, team_id, lock=True)
    views = member_views(team)
    check_can_leave(actor.id, views)
    admin_before = resolve_admin(views)
    membership = next(m for m in team.memberships if m.user_id == actor.id)
    team.memberships.remove(membership)
    if not team.memberships:
        team.status = "ARCHIVED"
    ctx.db.flush()
    record_event(
        ctx, action="MEMBER_LEFT", entity="team", entity_id=team.id, initiated_by=actor.id,
        before={"role": membership.role}, after={"status": team.status},
    )
    record_admin_change(ctx, team, admin_before, actor.id)
'@
Write-RivalText 'backend\app\services\neighborhood_service.py' @'
"""Catálogo de barrios: importación desde CSV y barrios dentro de un radio (ADR-006)."""

import csv
import io
from decimal import Decimal, InvalidOperation

from sqlalchemy import func, select

from app.domain.errors import DomainError
from app.domain.geo import haversine_km, validate_coordinates
from app.domain.identity_rules import validate_place_name
from app.domain.text_keys import search_key
from app.persistence.models_places import Neighborhood
from app.services.audit_service import record_event
from app.services.context import ServiceContext

EXPECTED_HEADER = ["nombre", "ciudad", "lat", "lon", "fuente"]
MAX_ROWS = 5000


def _parse_rows(text: str) -> list[tuple[str, str, Decimal, Decimal, str]]:
    reader = csv.reader(io.StringIO(text.lstrip("﻿")), delimiter=";")
    header = [h.strip().lower() for h in next(reader, [])]
    if header != EXPECTED_HEADER:
        raise DomainError("INVALID_CATALOG_FILE", f"El archivo debe empezar con: {';'.join(EXPECTED_HEADER)}")
    rows: list[tuple[str, str, Decimal, Decimal, str]] = []
    for number, raw in enumerate(reader, start=2):
        if not any(cell.strip() for cell in raw):
            continue
        if len(raw) != 5 or len(rows) >= MAX_ROWS:
            raise DomainError("INVALID_CATALOG_FILE", f"Fila {number}: se esperan 5 columnas (máximo {MAX_ROWS} filas).")
        name, city, lat_text, lon_text, source = (cell.strip() for cell in raw)
        try:
            lat, lon = Decimal(lat_text), Decimal(lon_text)
        except InvalidOperation as error:
            raise DomainError("INVALID_COORDINATES", f"Fila {number}: coordenadas no numéricas.") from error
        validate_coordinates(float(lat), float(lon))
        rows.append((validate_place_name(name, "barrio"), validate_place_name(city, "ciudad"), lat, lon, source[:120]))
    return rows


def import_csv(ctx: ServiceContext, text: str, imported_by: int | None = None) -> int:
    """Inserta o actualiza barrios por (ciudad, nombre). Devuelve cuántas filas procesó."""
    rows = _parse_rows(text)
    now = ctx.clock.now()
    for name, city, lat, lon, source in rows:
        key = (search_key(city), search_key(name))
        item = ctx.db.scalar(select(Neighborhood).where(
            Neighborhood.city_key == key[0], Neighborhood.name_key == key[1]))
        if item is None:
            item = Neighborhood(name=name, name_key=key[1], city=city, city_key=key[0])
            ctx.db.add(item)
        item.center_lat, item.center_lon = lat.quantize(Decimal("0.000001")), lon.quantize(Decimal("0.000001"))
        item.source, item.imported_at = source, now
    ctx.db.flush()
    record_event(ctx, action="NEIGHBORHOODS_IMPORTED", entity="neighborhood", entity_id="catalog",
                 initiated_by=imported_by, actor_type="HUMAN" if imported_by else "AUTOMATION",
                 after={"rows": len(rows)})
    return len(rows)


def catalog_size(ctx: ServiceContext) -> int:
    return ctx.db.scalar(select(func.count()).select_from(Neighborhood)) or 0


def center_of(ctx: ServiceContext, city: str, neighborhood: str) -> tuple[float, float] | None:
    item = ctx.db.scalar(select(Neighborhood).where(
        Neighborhood.city_key == search_key(city), Neighborhood.name_key == search_key(neighborhood)))
    return (float(item.center_lat), float(item.center_lon)) if item else None


def neighborhoods_within(ctx: ServiceContext, city: str, origin: str, radius_km: int) -> dict[str, float]:
    """Claves de barrio de la misma ciudad dentro del radio, con su distancia al barrio de origen."""
    center = center_of(ctx, city, origin)
    if center is None:
        return {}
    result: dict[str, float] = {}
    for item in ctx.db.scalars(select(Neighborhood).where(Neighborhood.city_key == search_key(city))):
        km = haversine_km(center[0], center[1], float(item.center_lat), float(item.center_lon))
        if km <= radius_km:
            result[item.name_key] = km
    return result
'@
Write-RivalText 'backend\app\services\passwords.py' @'
"""Hash de contraseñas con Argon2id según la guía de OWASP (19 MiB, 2 iteraciones, 1 hilo)."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_HASHER = PasswordHasher(time_cost=2, memory_cost=19 * 1024, parallelism=1)

# Hash de una contraseña que nadie conoce: se verifica contra él cuando el correo no existe,
# para que la respuesta tarde lo mismo y no revele si la cuenta existe.
_DUMMY_HASH = _HASHER.hash("rival-dummy-password-never-used")


def hash_password(password: str) -> str:
    return _HASHER.hash(password)


def verify_password(password_hash: str | None, password: str) -> bool:
    try:
        return _HASHER.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
    except (VerificationError, InvalidHashError):
        return False
'@
Write-RivalText 'backend\app\services\rate_limiter.py' @'
"""Límite de intentos de inicio de sesión con espera creciente.

Tras MAX_FAILURES fallos seguidos para la misma clave (correo + equipo cliente), el inicio
de sesión se bloquea BASE_LOCK_SECONDS y la espera se duplica en cada fallo adicional,
hasta MAX_LOCK_SECONDS. En memoria: suficiente para un solo proceso (Sprint 1);
con varios procesos se moverá a Redis (ADR-003).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock

from app.domain.errors import RateLimitedError

MAX_FAILURES = 5
BASE_LOCK_SECONDS = 30
MAX_LOCK_SECONDS = 15 * 60
MAX_TRACKED_KEYS = 10_000


@dataclass
class _Entry:
    failures: int = 0
    locked_until: datetime | None = None
    last_failure_at: datetime | None = None


class LoginRateLimiter:
    def __init__(self) -> None:
        self._entries: dict[str, _Entry] = {}
        self._lock = Lock()

    def check(self, key: str, now: datetime) -> None:
        with self._lock:
            entry = self._entries.get(key)
            if entry and entry.locked_until and entry.locked_until > now:
                wait = int((entry.locked_until - now).total_seconds()) + 1
                raise RateLimitedError(
                    "TOO_MANY_ATTEMPTS",
                    f"Demasiados intentos. Espera {wait} segundos e inténtalo de nuevo.",
                    retry_after_seconds=wait,
                )

    def register_failure(self, key: str, now: datetime) -> None:
        with self._lock:
            if len(self._entries) > MAX_TRACKED_KEYS:
                self._purge(now)
            entry = self._entries.setdefault(key, _Entry())
            entry.failures += 1
            entry.last_failure_at = now
            if entry.failures >= MAX_FAILURES:
                extra = entry.failures - MAX_FAILURES
                seconds = min(BASE_LOCK_SECONDS * (2**extra), MAX_LOCK_SECONDS)
                entry.locked_until = now + timedelta(seconds=seconds)

    def _purge(self, now: datetime) -> None:
        """Olvida claves sin bloqueo vigente y sin fallos recientes, para que la memoria no crezca sin tope."""
        horizon = timedelta(seconds=MAX_LOCK_SECONDS)
        stale = [
            k for k, e in self._entries.items()
            if (e.locked_until is None or e.locked_until <= now)
            and (e.last_failure_at is None or now - e.last_failure_at > horizon)
        ]
        for key in stale:
            del self._entries[key]

    def tracked_keys(self) -> int:
        return len(self._entries)

    def register_success(self, key: str) -> None:
        with self._lock:
            self._entries.pop(key, None)
'@
Write-RivalText 'backend\app\services\request_context.py' @'
"""Identificador de correlación por petición, para unir logs, errores y auditoría."""

import uuid
from contextvars import ContextVar

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="no-request")


def new_correlation_id() -> str:
    value = uuid.uuid4().hex
    _correlation_id.set(value)
    return value


def current_correlation_id() -> str:
    return _correlation_id.get()
'@
Write-RivalText 'backend\app\services\rival_service.py' @'
"""Buscar rivales del mismo deporte y modalidad por cercanía, barrio o ciudad (ADR-006).

Solo se devuelve el barrio, la ciudad y un rango de distancia; nunca coordenadas.
"""

from dataclasses import dataclass

from sqlalchemy import func, select

from app.domain.errors import DomainError, PermissionDeniedError
from app.domain.geo import DEFAULT_RADIUS_KM, DistanceBand, SearchScope, distance_band, validate_radius_km
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import Team
from app.services import neighborhood_service
from app.services.context import ServiceContext
from app.services.team_service import MAX_PAGE_SIZE, get_active_team, summary
from app.services.team_views import TeamSummaryView


@dataclass(frozen=True)
class RivalView:
    team: TeamSummaryView
    distance_band: DistanceBand | None


@dataclass(frozen=True)
class RivalPage:
    items: list[RivalView]
    page: int
    page_size: int
    total: int


def require_member(team: Team, actor: UserAccount) -> None:
    if not any(m.user_id == actor.id for m in team.memberships):
        raise PermissionDeniedError("MEMBERS_ONLY", "Solo los miembros del equipo pueden buscar en su nombre.")


def nearby_keys(ctx: ServiceContext, team: Team, radius_km: int) -> dict[str, float]:
    keys = neighborhood_service.neighborhoods_within(ctx, team.city, team.neighborhood, validate_radius_km(radius_km))
    if not keys:
        raise DomainError(
            "NEIGHBORHOOD_NOT_IN_CATALOG",
            "Tu barrio aún no tiene ubicación en el catálogo. Busca por barrio o por ciudad.",
        )
    return keys


def search_rivals(
    ctx: ServiceContext,
    actor: UserAccount,
    team_id: int,
    scope: SearchScope,
    radius_km: int = DEFAULT_RADIUS_KM,
    page: int = 1,
    page_size: int = 20,
) -> RivalPage:
    team = get_active_team(ctx, team_id)
    require_member(team, actor)
    page, page_size = max(1, page), max(1, min(page_size, MAX_PAGE_SIZE))
    stmt = select(Team).where(
        Team.status == "ACTIVE", Team.id != team.id, Team.sport_code == team.sport_code,
        Team.modality_code == team.modality_code, Team.city_key == team.city_key,
    )
    distances: dict[str, float] = {}
    if scope == SearchScope.NEIGHBORHOOD:
        stmt = stmt.where(Team.neighborhood_key == team.neighborhood_key)
    elif scope == SearchScope.NEARBY:
        distances = nearby_keys(ctx, team, radius_km)
        stmt = stmt.where(Team.neighborhood_key.in_(list(distances)))
    total = ctx.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(ctx.db.scalars(stmt.order_by(Team.name_key, Team.id)))
    if scope == SearchScope.NEARBY:
        rows.sort(key=lambda t: (distances[t.neighborhood_key], t.name_key))  # el más cercano primero
    chosen = rows[(page - 1) * page_size: page * page_size]
    items = [
        RivalView(team=summary(t), distance_band=distance_band(distances[t.neighborhood_key]) if distances else None)
        for t in chosen
    ]
    return RivalPage(items=items, page=page, page_size=page_size, total=total)
'@
Write-RivalText 'backend\app\services\team_service.py' @'
"""Casos de uso de equipos: crear, buscar, ver detalle y Mis equipos."""

from sqlalchemy import func, select

from app.domain.errors import DomainError, NotFoundError, PermissionDeniedError
from app.domain.identity_rules import validate_place_name
from app.domain.roles import ROLES_THAT_CAN_CREATE_TEAMS, TeamRole, UserRole
from app.domain.team_rules import MemberView, initial_team_role, resolve_admin
from app.domain.text_keys import search_key
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import JoinRequest, Team, TeamMembership
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.inputs import CreateTeamInput, TeamSearchInput
from app.services.team_views import MemberItem, MyTeamView, TeamDetailView, TeamPage, TeamSummaryView

MAX_PAGE_SIZE = 50


def get_active_team(ctx: ServiceContext, team_id: int, lock: bool = False) -> Team:
    """Con lock=True bloquea la fila del equipo (FOR UPDATE) para cambios de plantilla en serie."""
    team = ctx.db.get(Team, team_id, with_for_update=lock)
    if team is None or team.status != "ACTIVE":
        raise NotFoundError("TEAM_NOT_FOUND", "El equipo no existe o ya no está activo.")
    return team


def member_views(team: Team) -> list[MemberView]:
    return [MemberView(user_id=m.user_id, role=TeamRole(m.role)) for m in team.memberships]


def require_admin(team: Team, actor: UserAccount) -> None:
    if resolve_admin(member_views(team)) != actor.id:
        raise PermissionDeniedError(
            "ADMIN_ONLY", "Solo el administrador del equipo (DT o capitán) puede hacer esto."
        )


def resolve_admin_id(ctx: ServiceContext, team_id: int) -> int | None:
    team = ctx.db.get(Team, team_id)
    return resolve_admin(member_views(team)) if team else None


def record_admin_change(ctx: ServiceContext, team: Team, admin_before: int | None, actor_id: int) -> None:
    """El administrador se calcula; si una acción lo cambia, queda un evento propio en la auditoría."""
    admin_after = resolve_admin(member_views(team))
    if admin_after != admin_before and admin_after is not None:
        record_event(
            ctx, action="TEAM_ADMIN_CHANGED", entity="team", entity_id=team.id, initiated_by=actor_id,
            actor_type="SYSTEM_RULE", before={"admin": admin_before}, after={"admin": admin_after},
        )


def summary(team: Team) -> TeamSummaryView:
    return TeamSummaryView(
        id=team.id, name=team.name, sport_code=team.sport_code, modality_code=team.modality_code,
        city=team.city, neighborhood=team.neighborhood, member_count=len(team.memberships),
        has_coach=any(m.role == TeamRole.COACH for m in team.memberships),
    )


def create_team(ctx: ServiceContext, actor: UserAccount, data: CreateTeamInput) -> Team:
    roles = {UserRole(r.role) for r in actor.roles}
    if not roles & ROLES_THAT_CAN_CREATE_TEAMS:
        raise PermissionDeniedError("ROLE_CANNOT_CREATE_TEAM", "Agrega el rol de jugador o DT para crear un equipo.")
    if data.as_coach and UserRole.COACH not in roles:
        raise PermissionDeniedError("COACH_ROLE_REQUIRED", "Para entrar como DT agrega el rol de director técnico.")
    if not ctx.catalog.has_modality(data.sport_code, data.modality_code):
        raise DomainError("UNKNOWN_MODALITY", "Esa modalidad no corresponde al deporte elegido.")
    name = data.name.strip()
    if not 2 <= len(name) <= 60:
        raise DomainError("INVALID_TEAM_NAME", "El nombre del equipo debe tener entre 2 y 60 caracteres.")
    city = validate_place_name(data.city, "ciudad")
    neighborhood = validate_place_name(data.neighborhood, "barrio")
    now = ctx.clock.now()
    role = initial_team_role(UserRole.COACH if data.as_coach else UserRole.PLAYER)
    team = Team(
        name=name, name_key=search_key(name), sport_code=data.sport_code, modality_code=data.modality_code,
        city=city, city_key=search_key(city), neighborhood=neighborhood, neighborhood_key=search_key(neighborhood),
        created_by=actor.id, created_at=now,
        memberships=[TeamMembership(user_id=actor.id, role=role.value, joined_at=now)],
    )
    ctx.db.add(team)
    ctx.db.flush()
    record_event(
        ctx, action="TEAM_CREATED", entity="team", entity_id=team.id, initiated_by=actor.id,
        after={"name": team.name, "sport": team.sport_code, "modality": team.modality_code, "creator_role": role.value},
    )
    return team


def search_teams(ctx: ServiceContext, query: TeamSearchInput) -> TeamPage:
    page_size = max(1, min(query.page_size, MAX_PAGE_SIZE))
    page = max(1, query.page)
    stmt = select(Team).where(Team.status == "ACTIVE")
    if query.sport_code:
        stmt = stmt.where(Team.sport_code == query.sport_code)
    if query.modality_code:
        stmt = stmt.where(Team.modality_code == query.modality_code)
    if query.city:
        stmt = stmt.where(Team.city_key == search_key(query.city))
    if query.query:
        stmt = stmt.where(Team.name_key.contains(search_key(query.query), autoescape=True))
    total = ctx.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = ctx.db.scalars(stmt.order_by(Team.name_key, Team.id).offset((page - 1) * page_size).limit(page_size))
    return TeamPage(items=[summary(t) for t in rows], page=page, page_size=page_size, total=total)


def team_detail(ctx: ServiceContext, team_id: int) -> TeamDetailView:
    team = get_active_team(ctx, team_id)
    users = {u.id: u for u in ctx.db.scalars(
        select(UserAccount).where(UserAccount.id.in_([m.user_id for m in team.memberships]))
    )}
    members = [
        MemberItem(user_id=m.user_id, display_name=users[m.user_id].display_name,
                   role=TeamRole(m.role), position=users[m.user_id].position)
        for m in sorted(team.memberships, key=lambda m: (m.joined_at, m.id))
    ]
    return TeamDetailView(team=summary(team), admin_user_id=resolve_admin(member_views(team)), members=members)


def my_teams(ctx: ServiceContext, actor: UserAccount) -> list[MyTeamView]:
    memberships = ctx.db.scalars(
        select(TeamMembership).join(Team).where(TeamMembership.user_id == actor.id, Team.status == "ACTIVE")
    ).all()
    result: list[MyTeamView] = []
    for membership in memberships:
        team = membership.team
        is_admin = resolve_admin(member_views(team)) == actor.id
        pending = 0
        if is_admin:
            pending = ctx.db.scalar(select(func.count()).select_from(JoinRequest).where(
                JoinRequest.team_id == team.id, JoinRequest.status == "PENDING",
                JoinRequest.direction == "REQUEST")) or 0
        result.append(MyTeamView(team=summary(team), my_role=TeamRole(membership.role),
                                 is_admin=is_admin, pending_requests=pending))
    return result
'@
Write-RivalText 'backend\app\services\team_views.py' @'
"""Vistas de lectura de equipos. Nunca incluyen correo, fecha de nacimiento ni ubicación exacta."""

from dataclasses import dataclass

from app.domain.roles import TeamRole


@dataclass(frozen=True)
class TeamSummaryView:
    id: int
    name: str
    sport_code: str
    modality_code: str
    city: str
    neighborhood: str
    member_count: int
    has_coach: bool


@dataclass(frozen=True)
class MemberItem:
    user_id: int
    display_name: str
    role: TeamRole
    position: str | None


@dataclass(frozen=True)
class TeamDetailView:
    team: TeamSummaryView
    admin_user_id: int | None
    members: list[MemberItem]


@dataclass(frozen=True)
class MyTeamView:
    team: TeamSummaryView
    my_role: TeamRole
    is_admin: bool
    pending_requests: int


@dataclass(frozen=True)
class TeamPage:
    items: list[TeamSummaryView]
    page: int
    page_size: int
    total: int


@dataclass(frozen=True)
class JoinRequestView:
    id: int
    team_id: int
    user_id: int
    display_name: str
    position: str | None
    desired_role: TeamRole
    message: str | None
    status: str
'@
Write-RivalText 'backend\app\settings.py' @'
"""Configuración por variables de entorno. Ningún secreto vive en el código."""

import os
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

DEFAULT_CATALOG = Path(__file__).resolve().parent / "config" / "sports.json"


def _origins() -> list[str]:
    raw = os.getenv("RIVAL_CORS_ORIGINS", "http://localhost:8081")
    return [o.strip() for o in raw.split(",") if o.strip() and o.strip() != "*"]


@dataclass
class Settings:
    database_url: str = field(default_factory=lambda: os.getenv("RIVAL_DATABASE_URL", "sqlite:///./rival_dev.db"))
    cors_origins: list[str] = field(default_factory=_origins)
    session_ttl: timedelta = field(
        default_factory=lambda: timedelta(hours=int(os.getenv("RIVAL_SESSION_TTL_HOURS", "168")))
    )
    session_idle: timedelta = field(
        default_factory=lambda: timedelta(hours=int(os.getenv("RIVAL_SESSION_IDLE_HOURS", "72")))
    )
    catalog_path: Path = DEFAULT_CATALOG
    debug: bool = field(default_factory=lambda: os.getenv("RIVAL_DEBUG", "false").lower() == "true")
'@
Write-RivalText 'backend\app\tools\__init__.py' @'

'@
Write-RivalText 'backend\app\tools\import_neighborhoods.py' @'
"""Importa el catálogo de barrios desde un CSV (nombre;ciudad;lat;lon;fuente).

Uso:  python -m app.tools.import_neighborhoods ruta\\barrios.csv
Usa RIVAL_DATABASE_URL igual que la API. Queda registrado en la auditoría como AUTOMATION.
"""

import sys
from datetime import timedelta
from pathlib import Path

from app.domain.sports_catalog import SportCatalog
from app.persistence.database import create_schema, make_engine, make_session_factory, session_scope
from app.services import neighborhood_service
from app.services.clock import SystemClock
from app.services.context import ServiceContext
from app.settings import Settings


def main(path: str) -> None:
    settings = Settings()
    engine = make_engine(settings.database_url)
    create_schema(engine)
    text = Path(path).read_text(encoding="utf-8")
    for session in session_scope(make_session_factory(engine)):
        ctx = ServiceContext(db=session, clock=SystemClock(), catalog=SportCatalog.load(settings.catalog_path),
                             session_ttl=timedelta(0), session_idle=timedelta(0))
        count = neighborhood_service.import_csv(ctx, text)
        print(f"Barrios importados o actualizados: {count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python -m app.tools.import_neighborhoods archivo.csv")
    main(sys.argv[1])
'@
Write-RivalText 'backend\pytest.ini' @'
[pytest]
testpaths = tests
pythonpath = .
'@
Write-RivalText 'backend\requirements-dev.txt' @'
-r requirements.txt
pytest==9.0.3
httpx==0.28.1
psycopg[binary]==3.2.12
'@
Write-RivalText 'backend\requirements.txt' @'
# Dependencias de ejecución (versiones fijas; revisar con pip-audit en cada versión)
fastapi==0.165.0
starlette==1.7.0
pydantic==2.13.5
pydantic_core==2.46.5
uvicorn==0.38.0
SQLAlchemy==2.0.44
argon2-cffi==25.1.0
argon2-cffi-bindings==26.2.0
'@
Write-RivalText 'backend\tests\__init__.py' @'

'@
Write-RivalText 'backend\tests\api\__init__.py' @'

'@
Write-RivalText 'backend\tests\api\conftest.py' @'
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.persistence.database import make_engine
from app.settings import Settings
from tests.conftest import TEST_DATABASE_URL, reset_schema


@pytest.fixture
def client() -> Iterator[TestClient]:
    if not TEST_DATABASE_URL.startswith("sqlite"):
        engine = make_engine(TEST_DATABASE_URL)
        reset_schema(engine)
        engine.dispose()
    app = create_app(Settings(database_url=TEST_DATABASE_URL))
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, email: str, role: str = "PLAYER") -> dict[str, object]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "mi equipo juega los sábados",
            "display_name": "José Peña",
            "birth_date": "1998-05-10",
            "role": role,
            "sports": ["FOOTBALL"],
            "city": "Barranquilla",
            "neighborhood": "El Prado",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def auth(token: object) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_team(client: TestClient, token: object, name: str = "Los Halcones") -> int:
    response = client.post(
        "/api/v1/teams",
        headers=auth(token),
        json={"name": name, "sport_code": "FOOTBALL", "modality_code": "F7",
              "city": "Barranquilla", "neighborhood": "El Prado"},
    )
    assert response.status_code == 201, response.text
    return int(response.json()["team"]["id"])
'@
Write-RivalText 'backend\tests\api\test_api_flow.py' @'
from tests.api.conftest import auth, create_team, register


def test_catalog_is_public(client):
    response = client.get("/api/v1/catalog/sports")
    assert response.status_code == 200
    assert any(s["code"] == "FOOTBALL" for s in response.json()["sports"])


def test_register_returns_token_and_profile_without_password(client):
    body = register(client, "jugador@rival.test")
    assert body["token"]
    assert body["user"]["roles"] == ["PLAYER"]
    assert "password" not in str(body).lower()


def test_minor_rejected_with_spanish_message_and_correlation(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "menor@rival.test", "password": "mi equipo juega los sábados", "display_name": "Ana",
        "birth_date": "2012-01-01", "role": "PLAYER", "sports": ["FOOTBALL"],
        "city": "Barranquilla", "neighborhood": "El Prado"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "UNDERAGE"
    assert "18" in body["message"]
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]


def test_unknown_field_rejected(client):
    response = client.post("/api/v1/auth/register", json={"email": "x@rival.test", "is_admin": True})
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_requires_token(client):
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert response.json()["code"] == "SESSION_EXPIRED"


def test_full_join_flow(client):
    captain = register(client, "cap@rival.test")
    player = register(client, "jug@rival.test")
    team_id = create_team(client, captain["token"])
    found = client.get("/api/v1/teams", params={"city": "barranquilla"}, headers=auth(player["token"]))
    assert found.json()["total"] == 1
    request = client.post(f"/api/v1/teams/{team_id}/join-requests", headers=auth(player["token"]), json={})
    assert request.status_code == 201
    again = client.post(f"/api/v1/teams/{team_id}/join-requests", headers=auth(player["token"]), json={})
    assert again.status_code == 409
    pending = client.get(f"/api/v1/teams/{team_id}/join-requests", headers=auth(captain["token"]))
    request_id = pending.json()[0]["id"]
    approved = client.post(f"/api/v1/join-requests/{request_id}/approve", headers=auth(captain["token"]))
    assert approved.status_code == 200
    mine = client.get("/api/v1/me/teams", headers=auth(player["token"])).json()
    assert mine[0]["team"]["name"] == "Los Halcones"
    assert mine[0]["is_admin"] is False


def test_idor_cannot_approve_other_team_request(client):
    captain_a = register(client, "a@rival.test")
    captain_b = register(client, "b@rival.test")
    player = register(client, "jug@rival.test")
    team_a = create_team(client, captain_a["token"], "Equipo A")
    create_team(client, captain_b["token"], "Equipo B")
    client.post(f"/api/v1/teams/{team_a}/join-requests", headers=auth(player["token"]), json={})
    listing = client.get(f"/api/v1/teams/{team_a}/join-requests", headers=auth(captain_b["token"]))
    assert listing.status_code == 403
    approve = client.post("/api/v1/join-requests/1/approve", headers=auth(captain_b["token"]))
    assert approve.status_code == 403


def test_team_detail_hides_private_data(client):
    captain = register(client, "cap@rival.test")
    team_id = create_team(client, captain["token"])
    detail = client.get(f"/api/v1/teams/{team_id}", headers=auth(captain["token"])).json()
    text = str(detail)
    assert "cap@rival.test" not in text
    assert "1998" not in text
    assert detail["admin_user_id"] == captain["user"]["id"]


def test_login_lockout_returns_429_with_retry_after(client):
    register(client, "jug@rival.test")
    for _ in range(5):
        client.post("/api/v1/auth/login", json={"email": "jug@rival.test", "password": "clave equivocada"})
    locked = client.post("/api/v1/auth/login", json={"email": "jug@rival.test", "password": "mi equipo juega los sábados"})
    assert locked.status_code == 429
    assert int(locked.headers["Retry-After"]) > 0


def test_logout_invalidates_session(client):
    user = register(client, "jug@rival.test")
    assert client.post("/api/v1/auth/logout", headers=auth(user["token"])).status_code == 204
    assert client.get("/api/v1/me", headers=auth(user["token"])).status_code == 401


def test_security_headers_present(client):
    response = client.get("/api/v1/catalog/sports")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "no-store"


def test_unknown_team_returns_404(client):
    user = register(client, "jug@rival.test")
    response = client.get("/api/v1/teams/999", headers=auth(user["token"]))
    assert response.status_code == 404
    assert response.json()["code"] == "TEAM_NOT_FOUND"


def test_register_is_limited_per_ip(client):
    for i in range(10):
        register(client, f"persona{i}@rival.test")
    response = client.post("/api/v1/auth/register", json={
        "email": "once@rival.test", "password": "mi equipo juega los sábados", "display_name": "Ana",
        "birth_date": "1998-01-01", "role": "PLAYER", "sports": ["FOOTBALL"],
        "city": "Barranquilla", "neighborhood": "El Prado"})
    assert response.status_code == 429
'@
Write-RivalText 'backend\tests\api\test_api_sprint2.py' @'
"""API del Sprint 2 con catálogo SINTÉTICO [SIMULACIÓN]."""

from datetime import UTC, datetime, timedelta

from app.services import neighborhood_service
from app.services.clock import SystemClock
from app.services.context import ServiceContext
from tests.api.conftest import auth, register
from tests.conftest import CATALOG
from tests.services.test_neighborhood_service import SYNTHETIC_CSV


def seed_catalog(client) -> None:
    with client.app.state.session_factory() as session:
        ctx = ServiceContext(db=session, clock=SystemClock(), catalog=CATALOG,
                             session_ttl=timedelta(days=1), session_idle=timedelta(days=1))
        neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
        session.commit()


def team(client, token, name, barrio) -> int:
    response = client.post("/api/v1/teams", headers=auth(token), json={
        "name": name, "sport_code": "FOOTBALL", "modality_code": "F7",
        "city": "Ciudad Prueba", "neighborhood": barrio})
    assert response.status_code == 201, response.text
    return int(response.json()["team"]["id"])


def test_rivals_nearby_show_band_never_coordinates(client):
    seed_catalog(client)
    a, b = register(client, "a@r.test"), register(client, "b@r.test")
    team_a = team(client, a["token"], "Águilas", "Barrio Uno")
    team(client, b["token"], "Bravos", "Barrio Dos")
    response = client.get(f"/api/v1/teams/{team_a}/rivals", params={"scope": "NEARBY", "radius_km": 5},
                          headers=auth(a["token"]))
    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["distance_band"] == "UNDER_2_KM"
    assert "lat" not in response.text and "lon" not in response.text


def test_free_agent_invitation_flow(client):
    captain, player = register(client, "cap@r.test"), register(client, "libre@r.test")
    team_id = team(client, captain["token"], "Halcones", "Barrio Uno")
    client.post("/api/v1/me/free-agent", headers=auth(player["token"]),
                json={"sport_code": "FOOTBALL", "active": True, "position": "Arquero"})
    found = client.get("/api/v1/free-agents", params={"sport": "FOOTBALL", "city": "barranquilla"},
                       headers=auth(captain["token"])).json()
    assert found["items"][0]["position"] == "Arquero"
    invited = client.post(f"/api/v1/teams/{team_id}/invitations", headers=auth(captain["token"]),
                          json={"user_id": player["user"]["id"]})
    assert invited.status_code == 201
    invitation_id = client.get("/api/v1/me/invitations", headers=auth(player["token"])).json()[0]["id"]
    assert client.post(f"/api/v1/invitations/{invitation_id}/accept", headers=auth(captain["token"])).status_code == 404
    assert client.post(f"/api/v1/invitations/{invitation_id}/accept", headers=auth(player["token"])).status_code == 200


def test_match_request_offer_accept_flow(client):
    a, b = register(client, "a@r.test"), register(client, "b@r.test")
    team_a, team_b = team(client, a["token"], "Águilas", "Barrio Uno"), team(client, b["token"], "Bravos", "Barrio Dos")
    start = datetime.now(UTC) + timedelta(days=1)
    created = client.post(f"/api/v1/teams/{team_a}/match-requests", headers=auth(a["token"]), json={
        "window_start": start.isoformat(), "window_end": (start + timedelta(days=2)).isoformat(),
        "scope": "CITY", "referee_mode": "EITHER", "place_kind": "INFORMAL", "place_note": "Parque"})
    assert created.status_code == 201, created.text
    request_id = created.json()["id"]
    feed = client.get(f"/api/v1/teams/{team_b}/match-feed", headers=auth(b["token"])).json()
    assert [r["id"] for r in feed] == [request_id]
    offer = client.post(f"/api/v1/teams/{team_b}/match-requests/{request_id}/offers", headers=auth(b["token"]), json={
        "proposed_start": (start + timedelta(hours=5)).isoformat(), "referee_mode": "WITHOUT", "place_kind": "INFORMAL"})
    assert offer.status_code == 201, offer.text
    accepted = client.post(f"/api/v1/offers/{offer.json()['id']}/accept", headers=auth(a["token"]))
    assert accepted.json()["status"] == "ACCEPTED"
    mine = client.get(f"/api/v1/teams/{team_a}/match-requests", headers=auth(a["token"])).json()
    assert mine[0]["status"] == "MATCHED"


def test_naive_datetime_rejected(client):
    a = register(client, "a@r.test")
    team_a = team(client, a["token"], "Águilas", "Barrio Uno")
    response = client.post(f"/api/v1/teams/{team_a}/match-requests", headers=auth(a["token"]), json={
        "window_start": "2030-01-01T10:00:00", "window_end": "2030-01-02T10:00:00",
        "scope": "CITY", "referee_mode": "EITHER", "place_kind": "TO_AGREE"})
    assert response.status_code == 422


def test_search_quota_per_user(client):
    a = register(client, "a@r.test")
    team_a = team(client, a["token"], "Águilas", "Barrio Uno")
    statuses = [client.get(f"/api/v1/teams/{team_a}/rivals", headers=auth(a["token"])).status_code for _ in range(61)]
    assert statuses[:60] == [200] * 60
    assert statuses[60] == 429
'@
Write-RivalText 'backend\tests\conftest.py' @'
import os
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.domain.roles import UserRole
from app.domain.sports_catalog import SportCatalog
from app.persistence.database import Base, create_schema, load_models, make_engine, make_session_factory
from app.services.clock import FixedClock
from app.services.context import ServiceContext
from app.services.inputs import RegisterInput

# Con RIVAL_TEST_DATABASE_URL (p. ej. postgresql+psycopg://rival:rival_dev@127.0.0.1/rival_test)
# las mismas pruebas corren contra PostgreSQL; sin ella, contra SQLite en memoria.
TEST_DATABASE_URL = os.getenv("RIVAL_TEST_DATABASE_URL", "sqlite:///:memory:")

CATALOG = SportCatalog.load(Path(__file__).resolve().parents[1] / "app" / "config" / "sports.json")


def reset_schema(engine: object) -> None:
    load_models()
    Base.metadata.drop_all(engine)  # type: ignore[arg-type]
    create_schema(engine)  # type: ignore[arg-type]


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 11, 23, 15, 0, tzinfo=UTC))


@pytest.fixture
def db() -> Iterator[Session]:
    engine = make_engine(TEST_DATABASE_URL)
    reset_schema(engine)
    session = make_session_factory(engine)()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def ctx(db: Session, clock: FixedClock) -> ServiceContext:
    return ServiceContext(
        db=db,
        clock=clock,
        catalog=CATALOG,
        session_ttl=timedelta(days=7),
        session_idle=timedelta(hours=72),
    )


def register_input(
    email: str = "jugador@rival.test",
    role: UserRole = UserRole.PLAYER,
    birth_date: date = date(1998, 5, 10),
) -> RegisterInput:
    return RegisterInput(
        email=email,
        password="mi equipo juega los sábados",
        display_name="José Peña",
        birth_date=birth_date,
        role=role,
        sports=["FOOTBALL"],
        city="Barranquilla",
        neighborhood="El Prado",
        position="Delantero",
    )
'@
Write-RivalText 'backend\tests\domain\__init__.py' @'

'@
Write-RivalText 'backend\tests\domain\test_age_policy.py' @'
from datetime import date

from app.domain.age_policy import MIN_AGE_YEARS, is_adult


def test_min_age_is_18():
    assert MIN_AGE_YEARS == 18


def test_is_adult_turns_18_on_birthday():
    assert is_adult(date(2008, 11, 23), today=date(2026, 11, 23)) is True


def test_is_not_adult_day_before_birthday():
    assert is_adult(date(2008, 11, 24), today=date(2026, 11, 23)) is False


def test_leap_day_birthday_not_adult_on_feb_28():
    assert is_adult(date(2008, 2, 29), today=date(2026, 2, 28)) is False


def test_leap_day_birthday_adult_on_march_first():
    assert is_adult(date(2008, 2, 29), today=date(2026, 3, 1)) is True


def test_future_birth_date_is_not_adult():
    assert is_adult(date(2030, 1, 1), today=date(2026, 11, 23)) is False
'@
Write-RivalText 'backend\tests\domain\test_geo.py' @'
import pytest

from app.domain.errors import DomainError
from app.domain.geo import DistanceBand, distance_band, haversine_km, validate_coordinates, validate_radius_km


def test_haversine_zero_for_same_point():
    assert haversine_km(10.98, -74.80, 10.98, -74.80) == 0


def test_haversine_one_degree_latitude_is_about_111_km():
    assert haversine_km(10.0, -74.8, 11.0, -74.8) == pytest.approx(111.19, abs=0.1)


@pytest.mark.parametrize(
    ("km", "band"),
    [(0.0, DistanceBand.UNDER_2_KM), (1.99, DistanceBand.UNDER_2_KM), (2.0, DistanceBand.FROM_2_TO_5_KM),
     (5.0, DistanceBand.FROM_2_TO_5_KM), (5.01, DistanceBand.OVER_5_KM)],
)
def test_distance_band_boundaries(km, band):
    assert distance_band(km) == band


def test_radius_outside_limits_rejected():
    with pytest.raises(DomainError) as error:
        validate_radius_km(40)
    assert error.value.code == "INVALID_RADIUS"
    assert validate_radius_km(5) == 5


def test_invalid_coordinates_rejected():
    with pytest.raises(DomainError):
        validate_coordinates(95.0, -74.8)
'@
Write-RivalText 'backend\tests\domain\test_identity_rules.py' @'
import pytest

from app.domain.errors import DomainError
from app.domain.identity_rules import (
    MIN_PASSWORD_LENGTH,
    normalize_email,
    validate_display_name,
    validate_password,
    validate_place_name,
)


def test_email_is_trimmed_and_lowercased():
    assert normalize_email("  Sergio.Rodriguez@Example.COM ") == "sergio.rodriguez@example.com"


def test_invalid_email_rejected():
    with pytest.raises(DomainError) as error:
        normalize_email("sin-arroba")
    assert error.value.code == "INVALID_EMAIL"


def test_display_name_accepts_tildes_and_enie():
    assert validate_display_name("  José Peña Ñañez ") == "José Peña Ñañez"


def test_display_name_too_short_rejected():
    with pytest.raises(DomainError):
        validate_display_name("J")


def test_password_minimum_length():
    with pytest.raises(DomainError) as error:
        validate_password("a" * (MIN_PASSWORD_LENGTH - 1))
    assert error.value.code == "WEAK_PASSWORD"


def test_common_password_rejected():
    with pytest.raises(DomainError):
        validate_password("contraseña123")


def test_long_passphrase_with_spaces_accepted():
    validate_password("mi equipo juega los sábados")


def test_place_name_rejects_empty():
    with pytest.raises(DomainError) as error:
        validate_place_name("   ", field="barrio")
    assert error.value.code == "INVALID_PLACE"


def test_place_name_keeps_accents():
    assert validate_place_name(" El Prado ", field="barrio") == "El Prado"
'@
Write-RivalText 'backend\tests\domain\test_match_rules.py' @'
from datetime import UTC, datetime, timedelta

import pytest

from app.domain.errors import DomainError
from app.domain.match_rules import RefereeMode, check_offer_referee, check_proposed_start, validate_window

NOW = datetime(2026, 11, 23, 15, 0, tzinfo=UTC)


def test_valid_window():
    validate_window(NOW + timedelta(days=1), NOW + timedelta(days=3), NOW)


@pytest.mark.parametrize(
    ("start", "end", "code"),
    [
        (NOW - timedelta(hours=1), NOW + timedelta(days=1), "WINDOW_IN_PAST"),
        (NOW + timedelta(days=2), NOW + timedelta(days=1), "WINDOW_INVERTED"),
        (NOW + timedelta(days=1), NOW + timedelta(days=16), "WINDOW_TOO_LONG"),
        (NOW + timedelta(days=61), NOW + timedelta(days=62), "WINDOW_TOO_FAR"),
    ],
)
def test_invalid_windows(start, end, code):
    with pytest.raises(DomainError) as error:
        validate_window(start, end, NOW)
    assert error.value.code == code


def test_proposed_start_must_fall_inside_window():
    start, end = NOW + timedelta(days=1), NOW + timedelta(days=2)
    check_proposed_start(start, start, end, NOW)
    check_proposed_start(end, start, end, NOW)
    with pytest.raises(DomainError) as error:
        check_proposed_start(end + timedelta(minutes=1), start, end, NOW)
    assert error.value.code == "OFFER_OUTSIDE_WINDOW"
    with pytest.raises(DomainError) as past:
        check_proposed_start(start, start, end, start + timedelta(hours=1))
    assert past.value.code == "OFFER_IN_PAST"


def test_offer_must_choose_concrete_referee_mode_compatible_with_request():
    check_offer_referee(RefereeMode.EITHER, RefereeMode.WITHOUT)
    check_offer_referee(RefereeMode.WITH, RefereeMode.WITH)
    with pytest.raises(DomainError):
        check_offer_referee(RefereeMode.WITH, RefereeMode.WITHOUT)
    with pytest.raises(DomainError):
        check_offer_referee(RefereeMode.EITHER, RefereeMode.EITHER)
'@
Write-RivalText 'backend\tests\domain\test_sports_catalog.py' @'
from pathlib import Path

from app.domain.sports_catalog import SportCatalog

CATALOG_PATH = Path(__file__).resolve().parents[2] / "app" / "config" / "sports.json"


def test_catalog_loads_football_modalities():
    catalog = SportCatalog.load(CATALOG_PATH)
    assert catalog.has_modality("FOOTBALL", "F5")
    assert catalog.has_modality("FOOTBALL", "F11")


def test_catalog_includes_basketball_and_baseball():
    catalog = SportCatalog.load(CATALOG_PATH)
    assert catalog.has_sport("BASKETBALL")
    assert catalog.has_sport("BASEBALL")


def test_catalog_rejects_unknown_sport():
    catalog = SportCatalog.load(CATALOG_PATH)
    assert catalog.has_sport("QUIDDITCH") is False


def test_catalog_rejects_modality_of_other_sport():
    catalog = SportCatalog.load(CATALOG_PATH)
    assert catalog.has_modality("BASKETBALL", "F5") is False


def test_catalog_entries_have_spanish_names():
    catalog = SportCatalog.load(CATALOG_PATH)
    football = next(s for s in catalog.sports if s.code == "FOOTBALL")
    assert football.name == "Fútbol"
'@
Write-RivalText 'backend\tests\domain\test_team_rules.py' @'
import pytest

from app.domain.errors import DomainError
from app.domain.roles import TeamRole, UserRole
from app.domain.team_rules import (
    MemberView,
    check_can_leave,
    initial_team_role,
    resolve_admin,
)


def members(*pairs: tuple[int, TeamRole]) -> list[MemberView]:
    return [MemberView(user_id=uid, role=role) for uid, role in pairs]


def test_coach_creator_becomes_coach():
    assert initial_team_role(UserRole.COACH) == TeamRole.COACH


def test_player_creator_becomes_captain():
    assert initial_team_role(UserRole.PLAYER) == TeamRole.CAPTAIN


def test_admin_is_coach_when_present():
    roster = members((1, TeamRole.CAPTAIN), (2, TeamRole.COACH), (3, TeamRole.PLAYER))
    assert resolve_admin(roster) == 2


def test_admin_falls_back_to_captain():
    roster = members((1, TeamRole.PLAYER), (2, TeamRole.CAPTAIN))
    assert resolve_admin(roster) == 2


def test_no_admin_without_coach_or_captain():
    assert resolve_admin(members((1, TeamRole.PLAYER))) is None


def test_coach_cannot_leave_without_captain():
    roster = members((1, TeamRole.COACH), (2, TeamRole.PLAYER))
    with pytest.raises(DomainError) as error:
        check_can_leave(1, roster)
    assert error.value.code == "ADMIN_SUCCESSOR_REQUIRED"


def test_coach_can_leave_when_captain_exists():
    roster = members((1, TeamRole.COACH), (2, TeamRole.CAPTAIN))
    check_can_leave(1, roster)


def test_captain_admin_cannot_leave_with_teammates():
    roster = members((1, TeamRole.CAPTAIN), (2, TeamRole.PLAYER))
    with pytest.raises(DomainError) as error:
        check_can_leave(1, roster)
    assert error.value.code == "ADMIN_SUCCESSOR_REQUIRED"


def test_last_member_can_leave():
    check_can_leave(1, members((1, TeamRole.CAPTAIN)))


def test_player_can_always_leave():
    roster = members((1, TeamRole.COACH), (2, TeamRole.PLAYER))
    check_can_leave(2, roster)


def test_non_member_cannot_leave():
    with pytest.raises(DomainError) as error:
        check_can_leave(9, members((1, TeamRole.COACH)))
    assert error.value.code == "NOT_A_MEMBER"
'@
Write-RivalText 'backend\tests\domain\test_text_keys.py' @'
from app.domain.text_keys import search_key


def test_accents_and_case_are_ignored():
    assert search_key("  Bogotá ") == search_key("BOGOTA") == "bogota"


def test_enie_is_normalized_for_search():
    assert search_key("Peñas Blancas") == "penas blancas"
'@
Write-RivalText 'backend\tests\services\__init__.py' @'

'@
Write-RivalText 'backend\tests\services\match_helpers.py' @'
"""Ayudas para pruebas de partidos con catálogo SINTÉTICO [SIMULACIÓN]."""

from datetime import timedelta

from app.domain.geo import SearchScope
from app.domain.match_rules import PlaceKind, RefereeMode
from app.services import neighborhood_service
from app.services.match_views import MatchRequestInput, OfferInput
from tests.services.test_neighborhood_service import SYNTHETIC_CSV
from tests.services.test_rival_service import make_team


def setup_city(ctx):
    neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
    return {
        "uno": make_team(ctx, "uno@r.test", "Águilas", "Barrio Uno"),
        "dos": make_team(ctx, "dos@r.test", "Bravos", "Barrio Dos"),
        "tres": make_team(ctx, "tres@r.test", "Cóndores", "Barrio Tres"),
        "lejos": make_team(ctx, "lejos@r.test", "Lejanos", "Barrio Lejano"),
    }


def request_input(ctx, scope=SearchScope.NEARBY, radius=2, referee=RefereeMode.EITHER, target=None):
    now = ctx.clock.now()
    return MatchRequestInput(
        window_start=now + timedelta(days=1), window_end=now + timedelta(days=3), scope=scope,
        referee_mode=referee, place_kind=PlaceKind.INFORMAL, radius_km=radius if scope == SearchScope.NEARBY else None,
        target_team_id=target, place_note="Parque del barrio", message="Partido amistoso",
    )


def offer_input(ctx, hours=30, referee=RefereeMode.WITHOUT):
    return OfferInput(proposed_start=ctx.clock.now() + timedelta(hours=hours), referee_mode=referee,
                      place_kind=PlaceKind.INFORMAL, place_note="Cancha de arena")
'@
Write-RivalText 'backend\tests\services\test_audit_service.py' @'
from sqlalchemy import select

from app.persistence.models_audit import AuditEvent
from app.services import audit_service, auth_service
from tests.conftest import register_input


def test_registration_is_audited_with_actor(ctx):
    user = auth_service.register_user(ctx, register_input())
    events = ctx.db.scalars(select(AuditEvent)).all()
    assert [e.action for e in events] == ["USER_REGISTERED"]
    assert events[0].initiated_by == user.id
    assert events[0].actor_type == "HUMAN"
    assert "password" not in (events[0].after_json or "")


def test_chain_verifies_and_detects_tampering(ctx):
    auth_service.register_user(ctx, register_input(email="a@rival.test"))
    auth_service.register_user(ctx, register_input(email="b@rival.test"))
    assert audit_service.verify_chain(ctx.db) is True
    first = ctx.db.scalars(select(AuditEvent).order_by(AuditEvent.id)).first()
    first.after_json = '{"display_name": "Alterado"}'
    ctx.db.flush()
    assert audit_service.verify_chain(ctx.db) is False


def test_fork_with_same_prev_hash_is_rejected(ctx):
    import pytest
    from sqlalchemy.exc import IntegrityError

    auth_service.register_user(ctx, register_input())
    first = ctx.db.scalars(select(AuditEvent)).first()
    clone = AuditEvent(
        chain_position=99, occurred_at=first.occurred_at, actor_type="HUMAN", initiated_by=None,
        approved_by=None, action="FORK", entity="x", entity_id="1", before_json=None, after_json=None,
        correlation_id="c", software_version="0.1.0", prev_hash=first.prev_hash, integrity_hash="f" * 64,
    )
    ctx.db.add(clone)
    with pytest.raises(IntegrityError):
        ctx.db.flush()


def test_deleting_last_event_is_detected(ctx):
    auth_service.register_user(ctx, register_input(email="a@rival.test"))
    auth_service.register_user(ctx, register_input(email="b@rival.test"))
    last = ctx.db.scalars(select(AuditEvent).order_by(AuditEvent.chain_position.desc())).first()
    ctx.db.delete(last)
    ctx.db.flush()
    assert audit_service.verify_chain(ctx.db) is False
'@
Write-RivalText 'backend\tests\services\test_auth_service.py' @'
from datetime import date, timedelta

import pytest

from app.domain.errors import AuthenticationError, ConflictError, DomainError, RateLimitedError
from app.domain.roles import UserRole
from app.services import auth_service
from app.services.rate_limiter import LoginRateLimiter
from tests.conftest import register_input


def test_register_stores_hash_not_password(ctx):
    user = auth_service.register_user(ctx, register_input())
    assert user.password_hash.startswith("$argon2id$")
    assert "sábados" not in user.password_hash
    assert [r.role for r in user.roles] == ["PLAYER"]


def test_register_rejects_minor(ctx):
    with pytest.raises(DomainError) as error:
        auth_service.register_user(ctx, register_input(birth_date=date(2010, 1, 1)))
    assert error.value.code == "UNDERAGE"


def test_register_rejects_duplicate_email_case_insensitive(ctx):
    auth_service.register_user(ctx, register_input(email="dt@rival.test"))
    with pytest.raises(ConflictError) as error:
        auth_service.register_user(ctx, register_input(email="DT@Rival.test"))
    assert error.value.code == "EMAIL_TAKEN"


def test_register_rejects_unknown_sport(ctx):
    data = register_input()
    data.sports = ["QUIDDITCH"]
    with pytest.raises(DomainError) as error:
        auth_service.register_user(ctx, data)
    assert error.value.code == "UNKNOWN_SPORT"


def test_login_and_authenticate(ctx):
    auth_service.register_user(ctx, register_input())
    token, user = auth_service.login(ctx, LoginRateLimiter(), "jugador@rival.test", "mi equipo juega los sábados", "ip")
    assert auth_service.authenticate(ctx, token).id == user.id


def test_wrong_password_message_does_not_reveal_user(ctx):
    limiter = LoginRateLimiter()
    with pytest.raises(AuthenticationError) as unknown:
        auth_service.login(ctx, limiter, "nadie@rival.test", "cualquier cosa larga", "ip")
    auth_service.register_user(ctx, register_input())
    with pytest.raises(AuthenticationError) as wrong:
        auth_service.login(ctx, limiter, "jugador@rival.test", "otra clave larga", "ip")
    assert unknown.value.message == wrong.value.message


def test_five_failures_lock_login(ctx):
    auth_service.register_user(ctx, register_input())
    limiter = LoginRateLimiter()
    for _ in range(5):
        with pytest.raises(AuthenticationError):
            auth_service.login(ctx, limiter, "jugador@rival.test", "clave equivocada", "ip")
    with pytest.raises(RateLimitedError) as error:
        auth_service.login(ctx, limiter, "jugador@rival.test", "mi equipo juega los sábados", "ip")
    assert error.value.retry_after_seconds > 0


def test_session_expires_after_idle(ctx, clock):
    auth_service.register_user(ctx, register_input())
    token, _ = auth_service.login(ctx, LoginRateLimiter(), "jugador@rival.test", "mi equipo juega los sábados", "ip")
    clock.advance(timedelta(hours=73))
    with pytest.raises(AuthenticationError):
        auth_service.authenticate(ctx, token)


def test_logout_invalidates_token(ctx):
    auth_service.register_user(ctx, register_input())
    token, _ = auth_service.login(ctx, LoginRateLimiter(), "jugador@rival.test", "mi equipo juega los sábados", "ip")
    auth_service.logout(ctx, token)
    with pytest.raises(AuthenticationError):
        auth_service.authenticate(ctx, token)


def test_add_second_role(ctx):
    user = auth_service.register_user(ctx, register_input())
    auth_service.add_role(ctx, user, UserRole.REFEREE, ["FOOTBALL", "BASKETBALL"])
    assert sorted(r.role for r in user.roles) == ["PLAYER", "REFEREE"]
    assert sorted(s.sport_code for s in user.sports) == ["BASKETBALL", "FOOTBALL"]
'@
Write-RivalText 'backend\tests\services\test_concurrency_pg.py' @'
"""Concurrencia real: solo corre contra PostgreSQL (RIVAL_TEST_DATABASE_URL).

Dos administradores (o dos peticiones del mismo) actúan en el mismo instante; los
bloqueos FOR UPDATE y los índices únicos deben dejar pasar solo una acción.
"""

import threading
from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from app.domain.errors import DomainError
from app.domain.geo import SearchScope
from app.domain.roles import TeamRole, UserRole
from app.persistence.database import make_engine, make_session_factory
from app.services import audit_service, join_service, match_offer_service, match_request_service
from app.services.context import ServiceContext
from app.services.inputs import JoinRequestInput
from tests.conftest import CATALOG, TEST_DATABASE_URL, reset_schema
from tests.services.match_helpers import offer_input, request_input, setup_city
from tests.services.test_team_service import new_user, team_input

pytestmark = pytest.mark.skipif(TEST_DATABASE_URL.startswith("sqlite"), reason="requiere PostgreSQL")


def make_ctx(session: Session, clock) -> ServiceContext:
    return ServiceContext(db=session, clock=clock, catalog=CATALOG,
                          session_ttl=timedelta(days=7), session_idle=timedelta(hours=72))


def race(factory, clock, actions):
    """Ejecuta cada acción en su propia sesión, todas a la vez. Devuelve los códigos de error."""
    barrier = threading.Barrier(len(actions))
    outcomes: list[str] = []

    def run(action):
        with factory() as session:
            ctx = make_ctx(session, clock)
            barrier.wait()
            try:
                action(ctx)
                session.commit()
                outcomes.append("OK")
            except DomainError as error:
                session.rollback()
                outcomes.append(error.code)

    threads = [threading.Thread(target=run, args=(a,)) for a in actions]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    return sorted(outcomes)


@pytest.fixture
def factory():
    engine = make_engine(TEST_DATABASE_URL)
    reset_schema(engine)
    yield make_session_factory(engine)
    engine.dispose()


def test_two_offers_accepted_at_once_only_one_wins(factory, clock):
    with factory() as session:
        ctx = make_ctx(session, clock)
        city = setup_city(ctx)
        owner, team = city["uno"]
        request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
        a = match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
        b = match_offer_service.make_offer(ctx, city["tres"][0], city["tres"][1].id, request.id, offer_input(ctx))
        session.commit()
        ids = (owner.id, a.id, b.id)

    def accept(offer_id):
        return lambda ctx: match_offer_service.decide(ctx, ctx.db.get(type(owner), ids[0]), offer_id, accept=True)

    assert race(factory, clock, [accept(ids[1]), accept(ids[2])]) == ["MATCH_REQUEST_CLOSED", "OK"]
    with factory() as session:
        assert audit_service.verify_chain(session) is True


def test_two_coaches_approved_at_once_only_one_joins(factory, clock):
    with factory() as session:
        ctx = make_ctx(session, clock)
        from app.services import team_service

        captain = new_user(ctx, "cap@r.test")
        team = team_service.create_team(ctx, captain, team_input())
        reqs = [join_service.request_join(ctx, new_user(ctx, f"dt{i}@r.test", UserRole.COACH), team.id,
                                          JoinRequestInput(desired_role=TeamRole.COACH)) for i in range(2)]
        session.commit()
        ids = (captain.id, reqs[0].id, reqs[1].id)

    def approve(request_id):
        return lambda ctx: join_service.decide(ctx, ctx.db.get(type(captain), ids[0]), request_id, approve=True)

    outcomes = race(factory, clock, [approve(ids[1]), approve(ids[2])])
    # El segundo falla: o el equipo ya tiene DT, o el capitán dejó de administrar al entrar el primer DT.
    assert outcomes.count("OK") == 1
    assert set(outcomes) - {"OK"} <= {"TEAM_HAS_COACH", "ADMIN_ONLY"}
    with factory() as session:
        from app.services import team_service

        detail = team_service.team_detail(make_ctx(session, clock), team.id)
        assert [m.role for m in detail.members].count(TeamRole.COACH) == 1
        assert audit_service.verify_chain(session) is True


def test_accept_and_withdraw_at_once_stay_consistent(factory, clock):
    with factory() as session:
        ctx = make_ctx(session, clock)
        city = setup_city(ctx)
        owner, team = city["uno"]
        rival_owner, rival = city["dos"]
        request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
        offer = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx))
        session.commit()
        ids = (owner.id, rival_owner.id, offer.id, request.id)

    user = type(owner)
    accept = lambda ctx: match_offer_service.decide(ctx, ctx.db.get(user, ids[0]), ids[2], accept=True)  # noqa: E731
    withdraw = lambda ctx: match_offer_service.withdraw(ctx, ctx.db.get(user, ids[1]), ids[2])  # noqa: E731
    outcomes = race(factory, clock, [accept, withdraw])
    assert outcomes.count("OK") == 1 and set(outcomes) - {"OK"} == {"OFFER_NOT_PENDING"}
    with factory() as session:
        stored = match_request_service.get_request(make_ctx(session, clock), ids[3])
        offer_now = session.get(type(offer), ids[2])
        assert (stored.status == "MATCHED") == (offer_now.status == "ACCEPTED")
        assert audit_service.verify_chain(session) is True


def test_double_tap_accept_invitation_joins_once(factory, clock):
    from app.services import free_agent_service, invitation_service, team_service

    with factory() as session:
        ctx = make_ctx(session, clock)
        captain, player = new_user(ctx, "cap@r.test"), new_user(ctx, "libre@r.test")
        team = team_service.create_team(ctx, captain, team_input())
        free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
        invitation = invitation_service.invite(ctx, captain, team.id, player.id, None)
        session.commit()
        ids = (player.id, invitation.id)

    tap = lambda ctx: invitation_service.respond(ctx, ctx.db.get(type(player), ids[0]), ids[1], accept=True)  # noqa: E731
    assert race(factory, clock, [tap, tap]) == ["INVITATION_ALREADY_DECIDED", "OK"]
'@
Write-RivalText 'backend\tests\services\test_free_agents.py' @'
import pytest

from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.roles import TeamRole, UserRole
from app.services import free_agent_service, invitation_service, team_service
from app.services.inputs import TeamSearchInput
from tests.services.test_team_service import new_user, team_input


def test_player_marks_free_agent_and_appears_in_search(ctx):
    player = new_user(ctx, "libre@r.test")
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position="Arquero", note=None)
    scout = new_user(ctx, "dt@r.test", UserRole.COACH)
    page = free_agent_service.search(ctx, scout, sport_code="FOOTBALL", city="barranquilla")
    assert [(a.display_name, a.position, a.neighborhood) for a in page.items] == [("José Peña", "Arquero", "El Prado")]
    assert not hasattr(page.items[0], "email")


def test_inactive_profile_is_hidden(ctx):
    player = new_user(ctx, "libre@r.test")
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=False, position=None, note=None)
    assert free_agent_service.search(ctx, player, sport_code="FOOTBALL", city="Barranquilla").total == 0


def test_referee_cannot_be_free_agent(ctx):
    referee = new_user(ctx, "ref@r.test", UserRole.REFEREE)
    with pytest.raises(PermissionDeniedError):
        free_agent_service.set_free_agent(ctx, referee, "FOOTBALL", active=True, position=None, note=None)


def test_invitation_flow_requires_player_acceptance(ctx):
    captain = new_user(ctx, "cap@r.test")
    player = new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    invitation = invitation_service.invite(ctx, captain, team.id, player.id, "¿Juegas el sábado?")
    with pytest.raises(ConflictError):
        invitation_service.invite(ctx, captain, team.id, player.id, None)
    assert [i.team.name for i in invitation_service.my_invitations(ctx, player)] == ["Los Halcones"]
    with pytest.raises(NotFoundError):
        invitation_service.respond(ctx, captain, invitation.id, accept=True)
    invitation_service.respond(ctx, player, invitation.id, accept=True)
    roles = {m.user_id: m.role for m in team_service.team_detail(ctx, team.id).members}
    assert roles[player.id] == TeamRole.PLAYER
    assert free_agent_service.search(ctx, captain, sport_code="FOOTBALL", city="Barranquilla").total == 0


def test_cannot_invite_someone_not_free_agent(ctx):
    captain = new_user(ctx, "cap@r.test")
    other = new_user(ctx, "otro@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    with pytest.raises(ConflictError) as error:
        invitation_service.invite(ctx, captain, team.id, other.id, None)
    assert error.value.code == "NOT_A_FREE_AGENT"


def test_only_admin_invites(ctx):
    captain = new_user(ctx, "cap@r.test")
    outsider = new_user(ctx, "x@r.test")
    player = new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    with pytest.raises(PermissionDeniedError):
        invitation_service.invite(ctx, outsider, team.id, player.id, None)


def test_invitation_is_not_listed_as_join_request(ctx):
    from app.services import join_service

    captain = new_user(ctx, "cap@r.test")
    player = new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    invitation_service.invite(ctx, captain, team.id, player.id, None)
    assert join_service.list_requests(ctx, captain, team.id) == []
    assert team_service.search_teams(ctx, TeamSearchInput()).total == 1
'@
Write-RivalText 'backend\tests\services\test_limiters.py' @'
from datetime import UTC, datetime, timedelta

import pytest

from app.domain.errors import RateLimitedError
from app.services.ip_limiter import SlidingWindowLimiter
from app.services.rate_limiter import MAX_TRACKED_KEYS, LoginRateLimiter

NOW = datetime(2026, 11, 23, 15, 0, tzinfo=UTC)


def test_window_blocks_after_max_and_recovers():
    limiter = SlidingWindowLimiter(max_events=2, window=timedelta(minutes=1))
    limiter.hit("ip", NOW)
    limiter.hit("ip", NOW)
    with pytest.raises(RateLimitedError) as error:
        limiter.hit("ip", NOW)
    assert error.value.retry_after_seconds > 0
    limiter.hit("ip", NOW + timedelta(minutes=2))


def test_login_limiter_memory_is_bounded():
    limiter = LoginRateLimiter()
    for i in range(MAX_TRACKED_KEYS + 50):
        limiter.register_failure(f"correo{i}@x.test|ip", NOW)
    later = NOW + timedelta(hours=1)
    limiter.register_failure("otro@x.test|ip", later)
    assert limiter.tracked_keys() < 100
'@
Write-RivalText 'backend\tests\services\test_match_offers.py' @'
from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.domain.geo import SearchScope
from app.domain.match_rules import RefereeMode
from app.services import match_offer_service, match_request_service
from tests.services.match_helpers import offer_input, request_input, setup_city


@pytest.fixture
def scene(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    return city, request


def test_counter_offer_creates_new_version(ctx, scene):
    city, request = scene
    rival_owner, rival = city["dos"]
    first = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx, hours=30))
    second = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx, hours=40))
    assert (first.status, second.version) == ("SUPERSEDED", 2)


def test_offer_outside_window_or_wrong_referee_rejected(ctx, scene):
    city, request = scene
    rival_owner, rival = city["dos"]
    with pytest.raises(DomainError) as outside:
        match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx, hours=200))
    assert outside.value.code == "OFFER_OUTSIDE_WINDOW"
    with pytest.raises(DomainError) as referee:
        match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx, referee=RefereeMode.EITHER))
    assert referee.value.code == "REFEREE_MODE_REQUIRED"


def test_cannot_offer_to_own_request(ctx, scene):
    city, request = scene
    owner, team = city["uno"]
    with pytest.raises(ConflictError):
        match_offer_service.make_offer(ctx, owner, team.id, request.id, offer_input(ctx))


def test_accept_closes_request_and_supersedes_others(ctx, scene):
    city, request = scene
    owner, _ = city["uno"]
    winner = match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
    loser = match_offer_service.make_offer(ctx, city["tres"][0], city["tres"][1].id, request.id, offer_input(ctx))
    with pytest.raises(PermissionDeniedError):
        match_offer_service.decide(ctx, city["dos"][0], winner.id, accept=True)
    match_offer_service.decide(ctx, owner, winner.id, accept=True)
    assert (request.status, request.accepted_offer_id, loser.status) == ("MATCHED", winner.id, "SUPERSEDED")
    with pytest.raises(ConflictError):
        match_offer_service.make_offer(ctx, city["lejos"][0], city["lejos"][1].id, request.id, offer_input(ctx))


def test_withdraw_and_cancel(ctx, scene):
    city, request = scene
    owner, _ = city["uno"]
    offer = match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
    other = match_offer_service.make_offer(ctx, city["tres"][0], city["tres"][1].id, request.id, offer_input(ctx))
    match_offer_service.withdraw(ctx, city["dos"][0], offer.id)
    match_request_service.cancel_request(ctx, owner, request.id)
    assert (offer.status, other.status, request.status) == ("WITHDRAWN", "CANCELLED", "CANCELLED")


def test_offers_visibility(ctx, scene):
    city, request = scene
    owner, _ = city["uno"]
    match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
    match_offer_service.make_offer(ctx, city["tres"][0], city["tres"][1].id, request.id, offer_input(ctx))
    assert len(match_offer_service.list_offers(ctx, owner, request.id)) == 2
    assert [o.team.name for o in match_offer_service.list_offers(ctx, city["dos"][0], request.id)] == ["Bravos"]
    assert match_offer_service.list_offers(ctx, city["lejos"][0], request.id) == []


def test_cannot_accept_after_expiry(ctx, scene, clock):
    city, request = scene
    owner, _ = city["uno"]
    offer = match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
    clock.advance(timedelta(days=5))
    with pytest.raises(ConflictError) as error:
        match_offer_service.decide(ctx, owner, offer.id, accept=True)
    assert error.value.code == "MATCH_REQUEST_CLOSED"
'@
Write-RivalText 'backend\tests\services\test_match_requests.py' @'
from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.domain.geo import SearchScope
from app.services import match_feed_service, match_request_service
from tests.services.match_helpers import request_input, setup_city
from tests.services.test_team_service import new_user


def test_nearby_request_visible_only_within_radius(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    match_request_service.create_request(ctx, owner, team.id, request_input(ctx, radius=2))
    for key, expected in (("dos", 1), ("tres", 0), ("lejos", 0)):
        viewer, viewer_team = city[key]
        feed = match_feed_service.open_requests_for(ctx, viewer, viewer_team.id, SearchScope.CITY)
        assert len(feed) == expected, key
    viewer, viewer_team = city["dos"]
    item = match_feed_service.open_requests_for(ctx, viewer, viewer_team.id, SearchScope.CITY)[0]
    assert item.distance_band == "UNDER_2_KM"
    assert item.team.neighborhood == "Barrio Uno"


def test_city_request_visible_to_whole_city(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    viewer, viewer_team = city["lejos"]
    assert len(match_feed_service.open_requests_for(ctx, viewer, viewer_team.id, SearchScope.CITY)) == 1


def test_direct_challenge_only_seen_by_target(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    target_owner, target = city["lejos"]
    match_request_service.create_request(
        ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY, target=target.id))
    assert len(match_feed_service.open_requests_for(ctx, target_owner, target.id, SearchScope.NEIGHBORHOOD)) == 1
    other_owner, other = city["dos"]
    assert match_feed_service.open_requests_for(ctx, other_owner, other.id, SearchScope.CITY) == []


def test_only_admin_creates_requests(ctx):
    city = setup_city(ctx)
    _, team = city["uno"]
    outsider = new_user(ctx, "x@r.test")
    with pytest.raises(PermissionDeniedError):
        match_request_service.create_request(ctx, outsider, team.id, request_input(ctx))


def test_invalid_window_rejected(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    data = request_input(ctx)
    data.window_end = data.window_start - timedelta(hours=1)
    with pytest.raises(DomainError) as error:
        match_request_service.create_request(ctx, owner, team.id, data)
    assert error.value.code == "WINDOW_INVERTED"


def test_max_three_open_requests(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    for _ in range(3):
        match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    with pytest.raises(ConflictError) as error:
        match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    assert error.value.code == "TOO_MANY_OPEN_REQUESTS"


def test_expired_request_leaves_feed(ctx, clock):
    city = setup_city(ctx)
    owner, team = city["uno"]
    match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    clock.advance(timedelta(days=4))
    viewer, viewer_team = city["dos"]
    assert match_feed_service.open_requests_for(ctx, viewer, viewer_team.id, SearchScope.CITY) == []
    assert match_request_service.team_requests(ctx, owner, team.id)[0].status == "EXPIRED"
'@
Write-RivalText 'backend\tests\services\test_neighborhood_service.py' @'
"""Catálogo de barrios. Coordenadas SINTÉTICAS [SIMULACIÓN]: no son las reales de Barranquilla."""

import pytest

from app.domain.errors import DomainError
from app.services import neighborhood_service

SYNTHETIC_CSV = """nombre;ciudad;lat;lon;fuente
Barrio Uno;Ciudad Prueba;10.000000;-74.800000;sintetico
Barrio Dos;Ciudad Prueba;10.010000;-74.800000;sintetico
Barrio Tres;Ciudad Prueba;10.040000;-74.800000;sintetico
Barrio Lejano;Ciudad Prueba;10.200000;-74.800000;sintetico
Barrio Uno;Otra Ciudad;10.000000;-74.800000;sintetico
"""


def test_import_counts_rows_and_is_idempotent(ctx):
    assert neighborhood_service.import_csv(ctx, SYNTHETIC_CSV) == 5
    assert neighborhood_service.import_csv(ctx, SYNTHETIC_CSV) == 5
    assert neighborhood_service.catalog_size(ctx) == 5


def test_import_rejects_bad_coordinates(ctx):
    with pytest.raises(DomainError) as error:
        neighborhood_service.import_csv(ctx, "nombre;ciudad;lat;lon;fuente\nMalo;X;99;-74;s\n")
    assert error.value.code == "INVALID_COORDINATES"


def test_import_rejects_wrong_header(ctx):
    with pytest.raises(DomainError) as error:
        neighborhood_service.import_csv(ctx, "a,b,c\n1,2,3\n")
    assert error.value.code == "INVALID_CATALOG_FILE"


def test_neighborhoods_within_radius_same_city_only(ctx):
    neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
    found = neighborhood_service.neighborhoods_within(ctx, "Ciudad Prueba", "barrio uno", radius_km=5)
    assert set(found) == {"barrio uno", "barrio dos", "barrio tres"}
    assert found["barrio dos"] == pytest.approx(1.11, abs=0.05)


def test_unknown_origin_has_no_center(ctx):
    neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
    assert neighborhood_service.center_of(ctx, "Ciudad Prueba", "Sin Catalogo") is None
'@
Write-RivalText 'backend\tests\services\test_rival_service.py' @'
"""Búsqueda de rivales por cercanía, barrio o ciudad, con catálogo SINTÉTICO [SIMULACIÓN]."""

import pytest

from app.domain.errors import DomainError, PermissionDeniedError
from app.domain.geo import DistanceBand, SearchScope
from app.services import neighborhood_service, rival_service, team_service
from app.services.inputs import CreateTeamInput
from tests.services.test_neighborhood_service import SYNTHETIC_CSV
from tests.services.test_team_service import new_user


def make_team(ctx, email, name, barrio, modality="F7", sport="FOOTBALL"):
    owner = new_user(ctx, email)
    team = team_service.create_team(ctx, owner, CreateTeamInput(
        name=name, sport_code=sport, modality_code=modality, city="Ciudad Prueba", neighborhood=barrio))
    return owner, team


@pytest.fixture
def league(ctx):
    neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
    teams = {
        "a": make_team(ctx, "a@r.test", "Águilas", "Barrio Uno"),
        "b": make_team(ctx, "b@r.test", "Bravos", "Barrio Dos"),
        "c": make_team(ctx, "c@r.test", "Cóndores", "Barrio Lejano"),
        "d": make_team(ctx, "d@r.test", "Delfines", "Barrio Uno", modality="B5X5", sport="BASKETBALL"),
        "e": make_team(ctx, "e@r.test", "Escorpiones", "Barrio Uno", modality="F11"),
        "f": make_team(ctx, "f@r.test", "Fénix", "Barrio Uno"),
    }
    return teams


def names(page):
    return [r.team.name for r in page.items]


def test_nearby_returns_close_teams_with_band_only(ctx, league):
    owner, team = league["a"]
    page = rival_service.search_rivals(ctx, owner, team.id, SearchScope.NEARBY, radius_km=5)
    assert names(page) == ["Fénix", "Bravos"]
    assert [r.distance_band for r in page.items] == [DistanceBand.UNDER_2_KM, DistanceBand.UNDER_2_KM]


def test_neighborhood_scope_same_barrio(ctx, league):
    owner, team = league["a"]
    assert names(rival_service.search_rivals(ctx, owner, team.id, SearchScope.NEIGHBORHOOD)) == ["Fénix"]


def test_city_scope_excludes_other_sport_modality_and_self(ctx, league):
    owner, team = league["a"]
    page = rival_service.search_rivals(ctx, owner, team.id, SearchScope.CITY)
    assert names(page) == ["Bravos", "Cóndores", "Fénix"]
    assert page.total == 3


def test_nearby_without_catalog_center_explains(ctx, league):
    owner, team = make_team(ctx, "x@r.test", "Sin Mapa", "Barrio Nuevo")
    with pytest.raises(DomainError) as error:
        rival_service.search_rivals(ctx, owner, team.id, SearchScope.NEARBY, radius_km=5)
    assert error.value.code == "NEIGHBORHOOD_NOT_IN_CATALOG"


def test_only_members_search_as_team(ctx, league):
    _, team = league["a"]
    outsider = new_user(ctx, "out@r.test")
    with pytest.raises(PermissionDeniedError):
        rival_service.search_rivals(ctx, outsider, team.id, SearchScope.CITY)
'@
Write-RivalText 'backend\tests\services\test_sprint2_review_fixes.py' @'
"""Pruebas de los hallazgos de la revisión independiente del Sprint 2."""

from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError
from app.domain.geo import SearchScope
from app.services import (
    free_agent_service,
    invitation_service,
    join_service,
    match_offer_service,
    match_request_service,
    team_service,
)
from app.services.inputs import JoinRequestInput
from tests.services.match_helpers import offer_input, request_input, setup_city
from tests.services.test_team_service import new_user, team_input


def test_offer_outside_publisher_scope_is_not_found(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, radius=2))
    far_owner, far = city["lejos"]
    with pytest.raises(NotFoundError):
        match_offer_service.make_offer(ctx, far_owner, far.id, request.id, offer_input(ctx))
    other_city_owner = new_user(ctx, "otra@r.test")
    other = team_service.create_team(ctx, other_city_owner, team_input())
    with pytest.raises(NotFoundError):
        match_offer_service.make_offer(ctx, other_city_owner, other.id, request.id, offer_input(ctx))


def test_offer_in_the_past_rejected(ctx, clock):
    city = setup_city(ctx)
    owner, team = city["uno"]
    request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    clock.advance(timedelta(days=2))
    with pytest.raises(DomainError) as error:
        match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx, hours=-1))
    assert error.value.code == "OFFER_IN_PAST"


def test_version_keeps_growing_after_withdraw(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    rival_owner, rival = city["dos"]
    first = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx))
    match_offer_service.withdraw(ctx, rival_owner, first.id)
    again = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx))
    assert again.version == 2


def test_challenge_other_city_rejected(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    other = team_service.create_team(ctx, new_user(ctx, "otra@r.test"), team_input())
    with pytest.raises(DomainError) as error:
        match_request_service.create_request(
            ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY, target=other.id))
    assert error.value.code == "INVALID_CHALLENGE"


def test_admin_counter_ignores_invitations(ctx):
    captain, player = new_user(ctx, "cap@r.test"), new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    invitation_service.invite(ctx, captain, team.id, player.id, None)
    assert team_service.my_teams(ctx, captain)[0].pending_requests == 0


def test_joining_by_request_removes_free_agent(ctx):
    captain, player = new_user(ctx, "cap@r.test"), new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    request = join_service.request_join(ctx, player, team.id, JoinRequestInput())
    join_service.decide(ctx, captain, request.id, approve=True)
    assert free_agent_service.search(ctx, captain, sport_code="FOOTBALL", city="Barranquilla").total == 0


def test_reinvite_after_rejection_waits_a_week(ctx, clock):
    captain, player = new_user(ctx, "cap@r.test"), new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    first = invitation_service.invite(ctx, captain, team.id, player.id, None)
    invitation_service.respond(ctx, player, first.id, accept=False)
    with pytest.raises(ConflictError) as error:
        invitation_service.invite(ctx, captain, team.id, player.id, None)
    assert error.value.code == "INVITATION_COOLDOWN"
    clock.advance(timedelta(days=8))
    invitation_service.invite(ctx, captain, team.id, player.id, None)

'@
Write-RivalText 'backend\tests\services\test_team_admin_rules.py' @'
"""Reglas de administración y protecciones de la plantilla (revisión independiente del Sprint 1)."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.errors import PermissionDeniedError
from app.domain.roles import TeamRole, UserRole
from app.persistence.models_audit import AuditEvent
from app.persistence.models_teams import TeamMembership
from app.services import join_service, membership_service, team_service
from app.services.inputs import JoinRequestInput, TeamSearchInput
from tests.services.test_team_service import new_user, team_input


def test_approving_coach_records_admin_change(ctx):
    captain = new_user(ctx, "cap@rival.test")
    coach = new_user(ctx, "dt@rival.test", UserRole.COACH)
    team = team_service.create_team(ctx, captain, team_input())
    request = join_service.request_join(ctx, coach, team.id, JoinRequestInput(desired_role=TeamRole.COACH))
    join_service.decide(ctx, captain, request.id, approve=True)
    actions = [e.action for e in ctx.db.scalars(select(AuditEvent).order_by(AuditEvent.chain_position))]
    assert actions[-1] == "TEAM_ADMIN_CHANGED"


def test_captain_admin_naming_new_captain_hands_over_admin(ctx):
    captain = new_user(ctx, "cap@rival.test")
    player = new_user(ctx, "jug@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    join_service.decide(ctx, captain, join_service.request_join(ctx, player, team.id, JoinRequestInput()).id, True)
    membership_service.set_captain(ctx, captain, team.id, player.id)
    detail = team_service.team_detail(ctx, team.id)
    assert detail.admin_user_id == player.id
    assert [m.role for m in detail.members].count(TeamRole.CAPTAIN) == 1


def test_database_rejects_second_captain(ctx):
    captain = new_user(ctx, "cap@rival.test")
    other = new_user(ctx, "otro@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    ctx.db.add(TeamMembership(team_id=team.id, user_id=other.id, role="CAPTAIN", joined_at=ctx.clock.now()))
    with pytest.raises(IntegrityError):
        ctx.db.flush()


def test_referee_cannot_request_to_join(ctx):
    captain = new_user(ctx, "cap@rival.test")
    referee = new_user(ctx, "ref@rival.test", UserRole.REFEREE)
    team = team_service.create_team(ctx, captain, team_input())
    with pytest.raises(PermissionDeniedError) as error:
        join_service.request_join(ctx, referee, team.id, JoinRequestInput())
    assert error.value.code == "ROLE_CANNOT_JOIN_TEAM"


def test_search_treats_percent_literally(ctx):
    team_service.create_team(ctx, new_user(ctx, "a@rival.test"), team_input("Halcones"))
    assert team_service.search_teams(ctx, TeamSearchInput(query="%")).items == []
'@
Write-RivalText 'backend\tests\services\test_team_service.py' @'
import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.domain.roles import TeamRole, UserRole
from app.services import auth_service, join_service, membership_service, team_service
from app.services.inputs import CreateTeamInput, JoinRequestInput, TeamSearchInput
from tests.conftest import register_input


def new_user(ctx, email: str, role: UserRole = UserRole.PLAYER):
    return auth_service.register_user(ctx, register_input(email=email, role=role))


def team_input(name: str = "Los Halcones", as_coach: bool = False) -> CreateTeamInput:
    return CreateTeamInput(
        name=name, sport_code="FOOTBALL", modality_code="F7",
        city="Barranquilla", neighborhood="El Prado", as_coach=as_coach,
    )


def test_player_creates_team_as_captain_admin(ctx):
    user = new_user(ctx, "cap@rival.test")
    team = team_service.create_team(ctx, user, team_input())
    detail = team_service.team_detail(ctx, team.id)
    assert detail.admin_user_id == user.id
    assert detail.members[0].role == TeamRole.CAPTAIN


def test_coach_creates_team_as_coach(ctx):
    coach = new_user(ctx, "dt@rival.test", UserRole.COACH)
    team = team_service.create_team(ctx, coach, team_input(as_coach=True))
    assert team_service.team_detail(ctx, team.id).members[0].role == TeamRole.COACH


def test_player_cannot_create_as_coach(ctx):
    with pytest.raises(PermissionDeniedError):
        team_service.create_team(ctx, new_user(ctx, "p@rival.test"), team_input(as_coach=True))


def test_referee_cannot_create_team(ctx):
    referee = new_user(ctx, "ref@rival.test", UserRole.REFEREE)
    with pytest.raises(PermissionDeniedError):
        team_service.create_team(ctx, referee, team_input())


def test_unknown_modality_rejected(ctx):
    data = team_input()
    data.modality_code = "B3X3"
    with pytest.raises(DomainError) as error:
        team_service.create_team(ctx, new_user(ctx, "x@rival.test"), data)
    assert error.value.code == "UNKNOWN_MODALITY"


def test_search_filters_by_city_case_insensitive(ctx):
    team_service.create_team(ctx, new_user(ctx, "a@rival.test"), team_input("Halcones"))
    page = team_service.search_teams(ctx, TeamSearchInput(city="barranquilla", sport_code="FOOTBALL"))
    assert [t.name for t in page.items] == ["Halcones"]
    assert team_service.search_teams(ctx, TeamSearchInput(city="Cali")).items == []


def test_join_request_flow(ctx):
    captain = new_user(ctx, "cap@rival.test")
    player = new_user(ctx, "jug@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    request = join_service.request_join(ctx, player, team.id, JoinRequestInput())
    with pytest.raises(ConflictError) as error:
        join_service.request_join(ctx, player, team.id, JoinRequestInput())
    assert error.value.code == "REQUEST_ALREADY_PENDING"
    join_service.decide(ctx, captain, request.id, approve=True)
    roles = {m.user_id: m.role for m in team_service.team_detail(ctx, team.id).members}
    assert roles[player.id] == TeamRole.PLAYER


def test_only_admin_decides_requests(ctx):
    captain = new_user(ctx, "cap@rival.test")
    outsider = new_user(ctx, "otro@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    request = join_service.request_join(ctx, new_user(ctx, "jug@rival.test"), team.id, JoinRequestInput())
    with pytest.raises(PermissionDeniedError):
        join_service.decide(ctx, outsider, request.id, approve=True)
    with pytest.raises(PermissionDeniedError):
        join_service.list_requests(ctx, outsider, team.id)


def test_approved_coach_becomes_admin(ctx):
    captain = new_user(ctx, "cap@rival.test")
    coach = new_user(ctx, "dt@rival.test", UserRole.COACH)
    team = team_service.create_team(ctx, captain, team_input())
    request = join_service.request_join(ctx, coach, team.id, JoinRequestInput(desired_role=TeamRole.COACH))
    join_service.decide(ctx, captain, request.id, approve=True)
    assert team_service.team_detail(ctx, team.id).admin_user_id == coach.id


def test_member_cannot_request_again(ctx):
    captain = new_user(ctx, "cap@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    with pytest.raises(ConflictError):
        join_service.request_join(ctx, captain, team.id, JoinRequestInput())


def test_coach_leaving_without_captain_is_blocked_then_allowed(ctx):
    coach = new_user(ctx, "dt@rival.test", UserRole.COACH)
    player = new_user(ctx, "jug@rival.test")
    team = team_service.create_team(ctx, coach, team_input(as_coach=True))
    request = join_service.request_join(ctx, player, team.id, JoinRequestInput())
    join_service.decide(ctx, coach, request.id, approve=True)
    with pytest.raises(DomainError) as error:
        membership_service.leave_team(ctx, coach, team.id)
    assert error.value.code == "ADMIN_SUCCESSOR_REQUIRED"
    membership_service.set_captain(ctx, coach, team.id, player.id)
    membership_service.leave_team(ctx, coach, team.id)
    assert team_service.team_detail(ctx, team.id).admin_user_id == player.id


def test_last_member_leaving_archives_team(ctx):
    captain = new_user(ctx, "cap@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    membership_service.leave_team(ctx, captain, team.id)
    assert team_service.search_teams(ctx, TeamSearchInput()).items == []


def test_my_teams_lists_role_and_pending_count(ctx):
    captain = new_user(ctx, "cap@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    join_service.request_join(ctx, new_user(ctx, "jug@rival.test"), team.id, JoinRequestInput())
    mine = team_service.my_teams(ctx, captain)
    assert mine[0].is_admin is True
    assert mine[0].pending_requests == 1

'@
Write-RivalText 'docs\adr\ADR-001-cliente-movil-expo.md' @'
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
'@
Write-RivalText 'docs\adr\ADR-002-monolito-modular-fastapi.md' @'
# ADR-002 — Monolito modular con FastAPI

- **Fecha:** 23/11/2026
- **Estado:** Aceptada

## Contexto

Equipo pequeño, producto nuevo, reglas de dominio con muchas relaciones (equipos, ligas, contratos, árbitros, canchas). No hay evidencia de que haga falta escalar por separado ningún módulo.

## Opciones

- Monolito modular (un solo despliegue, módulos con límites claros).
- Microservicios (despliegues independientes, más infraestructura y fallos de red entre módulos).

## Decisión

Monolito modular FastAPI con capas `domain` (reglas puras, sin dependencias), `persistence` (SQLAlchemy), `services` (casos de uso, auditoría) y `api` (rutas y esquemas). Módulos previstos: identity, teams, leagues, matchmaking, match_contract, referees, venues, audit, health.

## Consecuencias

- Las reglas se prueban sin base de datos ni HTTP.
- Si un módulo necesita separarse, sus límites ya existen.
'@
Write-RivalText 'docs\adr\ADR-003-postgresql-postgis.md' @'
# ADR-003 — PostgreSQL + PostGIS como fuente de verdad

- **Fecha:** 23/11/2026
- **Estado:** Aceptada; SQLite solo en desarrollo del Sprint 1

## Contexto

La búsqueda por cercanía necesita consultas por radio con índice. PostGIS ofrece `geography(Point,4326)`, índices GiST y `ST_DWithin`, que usa el índice y es más rápida que `ST_Distance` (https://postgis.net/documentation/tips/st-dwithin, consultado 23/11/2026).

## Decisión

- Producción: PostgreSQL + PostGIS; Row Level Security como segunda barrera.
- Las distancias se calculan desde el centro del barrio (catálogo `neighborhood`), nunca desde la posición de una persona.
- Sprint 1 (sin búsqueda geográfica): SQLite para que el proyecto corra en Windows sin instalar nada más. La migración a PostgreSQL entra en el Sprint 2 con migraciones versionadas.
- Redis solo para caché, límites de peticiones y colas.

## Consecuencias

- El código de persistencia usa SQLAlchemy 2 sin funciones exclusivas de SQLite.
'@
Write-RivalText 'docs\adr\ADR-004-ubicacion-sin-posicion-exacta.md' @'
# ADR-004 — Ubicación por cercanía, barrio o ciudad; nunca posición exacta

- **Fecha:** 23/11/2026
- **Estado:** Aceptada (decisión del dueño del producto)

## Contexto

La ubicación es dato personal (Ley 1581 de 2012). Google Play solo aprueba ubicación en segundo plano cuando es la función principal y recomienda la ubicación en primer plano (https://support.google.com/googleplay/android-developer/answer/9799150, consultado 23/11/2026).

## Decisión

- Se guarda el barrio y la ciudad elegidos por el usuario, no coordenadas de personas.
- El GPS es opcional, solo "mientras se usa la app", y sirve para sugerir el barrio; la posición se descarta.
- Las distancias se muestran por rangos (menos de 2 km, 2 a 5 km, más de 5 km).
- Las búsquedas tienen límite de peticiones para impedir triangular la ubicación de alguien.
- Los establecimientos sí muestran su dirección.

## Consecuencias

- Sprint 1: ciudad y barrio como texto validado. Sprint 2: catálogo de barrios con centro geográfico.
'@
Write-RivalText 'docs\adr\ADR-005-rating-glicko2.md' @'
# ADR-005 — Rating de equipos con Glicko-2 (P1)

- **Fecha:** 23/11/2026
- **Estado:** Propuesta para P1

## Contexto

El emparejamiento debe sugerir rivales de nivel parecido. Un equipo nuevo no tiene historial.

## Decisión

Rating Glicko-2 por equipo y modalidad: además del nivel mide la incertidumbre (RD) y la volatilidad, de modo que un equipo nuevo tiene RD alta. Solo cuentan partidos con resultado confirmado por ambos administradores o por el árbitro.

## Consecuencias

- Hasta P1 el emparejamiento usa reglas deterministas (deporte, modalidad, alcance, franja horaria).
'@
Write-RivalText 'docs\adr\ADR-006-cercania-por-centro-de-barrio.md' @'
# ADR-006 — Cercanía calculada entre centros de barrio, sobre el catálogo

- **Fecha:** 23/11/2026
- **Estado:** Aceptada (precisa ADR-003 y ADR-004)

## Contexto

RIVAL nunca guarda la posición de una persona (ADR-004). Lo único con coordenadas es el catálogo de barrios: un punto central por barrio. Barranquilla, la ciudad piloto, tiene 177 barrios según el Anuario Estadístico 2020 de la Alcaldía (https://barranquilla.gov.co/documento/anuario-estadistico-2020-cap-2-territorio-y-medio-ambiente, consultado 23/11/2026).

## Opciones

| Opción | A favor | En contra |
| --- | --- | --- |
| `ST_DWithin` de PostGIS sobre la tabla de equipos | Índice GiST, escala a millones de puntos | Exige guardar un punto por equipo; solo corre en PostgreSQL con PostGIS |
| Distancia entre centros de barrio sobre el catálogo (haversine) y luego filtrar equipos por `neighborhood_id` | Funciona igual en SQLite y PostgreSQL; el catálogo tiene cientos de filas por ciudad; ningún equipo ni persona tiene coordenadas propias | Si el catálogo creciera a decenas de miles de barrios por consulta habría que moverlo a PostGIS |

## Decisión

1. La distancia se calcula entre el centro del barrio del equipo que busca y el centro de cada barrio del catálogo de la misma ciudad (fórmula de haversine, radio terrestre medio 6.371 km).
2. Los barrios dentro del radio se convierten en una lista de `neighborhood_id` y la consulta de equipos filtra por esa lista.
3. A las personas solo se les muestra el **rango**: "menos de 2 km", "2 a 5 km" o "más de 5 km".
4. Si un barrio no tiene coordenadas en el catálogo, "Cerca de mí" no lo incluye y la búsqueda sigue disponible por barrio y ciudad.
5. El catálogo se importa desde un CSV (`nombre;ciudad;lat;lon;fuente`). La fuente prevista para Barranquilla es el "Mapa de Barrios de Barranquilla Según el POT" en datos.gov.co [POR VERIFICAR: descargar y convertir a centroides]. Las pruebas usan barrios sintéticos rotulados [SIMULACIÓN].
6. PostGIS sigue siendo la base de producción (ADR-003) y se usará si el volumen lo exige.

## Consecuencias

- Las coordenadas del catálogo usan `Numeric(9,6)`; los cálculos de distancia usan `float` porque no son dinero.
- Las búsquedas por radio tienen límite de peticiones para impedir triangular dónde juega un equipo.
'@
Write-RivalText 'docs\sprint-01.md' @'
# Sprint 1 — Registro por rol, equipos y Mi equipo

- **Fecha:** 23/11/2026
- **Meta (PO):** una persona se registra con su rol y sus deportes, crea un equipo o pide entrar a uno, y ve Mi equipo.
- **Estado:** Implementado y verificado en el entorno de desarrollo; pendiente de prueba en emulador o teléfono.

## Historias cubiertas

| ID | Historia | Estado |
| --- | --- | --- |
| RIV-001 | Registro por rol (jugador, DT, árbitro, establecimiento) con deportes; menores rechazados | Verificado |
| RIV-002 | Agregar otro rol a la cuenta (`POST /me/roles`) | Verificado (API; sin pantalla aún) |
| RIV-003 | Buscar equipo o crearlo; solicitar unirse; el administrador aprueba | Verificado |
| RIV-004 | Mi equipo: plantilla, administrador, solicitudes | Verificado |
| RIV-005 | Sin DT, el capitán administra; traspaso auditado | Verificado |
| RIV-006 | Agentes libres | Pasa al Sprint 2 |

## Loop 4 — Verificación (salidas reales del 23/11/2026)

| Verificación | Comando | Resultado |
| --- | --- | --- |
| Pruebas backend | `python -m pytest -q` | 80 aprobadas, 0 fallidas |
| Tipos de la app | `npx tsc --noEmit` | 0 errores |
| Pruebas de reglas locales | `npm test` | 4 aprobadas |
| Empaquetado Android | `npx expo export --platform android` | Compila (bundle de 1,6 MB) |
| Servidor real | `uvicorn app.main:app` + registro con `curl` | Responde 201 con token; `/docs` cerrado fuera de depuración |
| Vulnerabilidades Python | `pip-audit -r requirements.txt` | Ninguna conocida |
| Vulnerabilidades npm | `npm audit --omit=dev` | 3 moderadas en herramientas de compilación de Expo (minimatch); la corrección automática bajaría Expo a la versión 52, así que no se aplicó |
| Líneas por archivo | conteo en `backend/` y `mobile/src` | Ninguno pasa de 150 |
| `any` y `TODO` | búsqueda en el código | Ninguno |
| App en emulador o teléfono | — | NO EJECUTADO (requiere tu equipo) |
| Accesibilidad con lector de pantalla | — | NO EJECUTADO |

## Revisión independiente

Un revisor que no escribió el código revisó el backend y la app. Confirmó que no hay IDOR, que no se filtran correos ni fechas de nacimiento, que no hay inyección SQL y que la regla de edad es correcta. Encontró estos problemas, ya corregidos con pruebas:

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| ALTO | La cadena de auditoría podía bifurcarse con escrituras simultáneas (en PostgreSQL) | Fila `audit_head` bloqueada con `FOR UPDATE`, `prev_hash` único, posición en la cadena y versión incluidas en el hash | `test_fork_with_same_prev_hash_is_rejected`, `test_deleting_last_event_is_detected` |
| MEDIO | Dos DT o dos capitanes posibles con peticiones simultáneas | Índices únicos parciales en la base y bloqueo de la fila del equipo | `test_database_rejects_second_captain` |
| MEDIO | El cambio de administrador no se auditaba al aprobar un DT o nombrar capitán | Evento `TEAM_ADMIN_CHANGED` siempre que cambia; aviso en la app antes de ceder la administración | `test_approving_coach_records_admin_change`, `test_captain_admin_naming_new_captain_hands_over_admin` |
| MEDIO | Registro e inicio de sesión sin límite por IP; memoria del limitador sin tope | Ventana deslizante por IP (10 registros/hora, 30 inicios/15 min) y purga | `test_register_is_limited_per_ip`, `test_login_limiter_memory_is_bounded` |
| MEDIO | App: una sesión vencida no cerraba la sesión | Manejador global de 401 | Revisión de código (sin pruebas de componentes aún) |
| MEDIO | App: el arranque podía quedarse cargando si falla el almacenamiento seguro | Lectura del token dentro del `try` | Revisión de código |
| MEDIO | App: el doble toque podía crear dos equipos | Cerrojo síncrono `useSubmitLock` | Revisión de código |
| MEDIO | App: la búsqueda no pedía la página 2 | Botón "Cargar más" | Revisión de código |
| BAJO | Árbitros o establecimientos podían unirse a un equipo | Requiere rol de jugador o DT | `test_referee_cannot_request_to_join` |
| BAJO | `%` y `_` actuaban como comodines en la búsqueda | `autoescape=True` | `test_search_treats_percent_literally` |
| BAJO | Registro simultáneo con el mismo correo daba 500 | Se captura y responde 409 | Revisión de código |
| BAJO | El tiempo límite no cubría la lectura de la respuesta | Se lee el cuerpo antes de soltar el temporizador | Revisión de código |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | El registro responde "correo ya existe", lo que permite saber si una cuenta existe (mitigado con el límite por IP) | Verificación por correo en el Sprint de endurecimiento |
| MEDIO | La app no tiene pruebas automáticas de componentes ni de hooks | Agregar `jest-expo` en el Sprint 2 |
| MEDIO | Los bloqueos de concurrencia solo se probaron en SQLite | Probar con PostgreSQL en el Sprint 2 |
| BAJO | Detrás de un proxy, la IP del límite debe venir de un encabezado de confianza [POR VERIFICAR] | Configurable al desplegar |
| BAJO | Las sesiones vencidas no se purgan | Tarea programada en el Sprint de endurecimiento |
| BAJO | Inicios de sesión fallidos no se auditan | Centro de salud (Sprint 4) |
| BAJO | La URL del backend es `http` en desarrollo | Exigir `https` en producción |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -v
cd mobile; npm run typecheck; npm test
```
'@
Write-RivalText 'docs\sprint-02.md' @'
# Sprint 2 — Rivales, retos, ofertas y agentes libres

- **Fecha:** 23/11/2026
- **Meta (PO):** un DT encuentra rival por cercanía, barrio o ciudad, lo reta o publica una búsqueda abierta que recibe ofertas al estilo InDriver; los jugadores sin equipo aparecen como agentes libres y aceptan invitaciones.
- **Estado:** Implementado y verificado en SQLite y PostgreSQL 16; pendiente de prueba en emulador o teléfono y del catálogo real de barrios.

## Historias cubiertas

| ID | Historia | Estado |
| --- | --- | --- |
| RIV-006 | Agentes libres por deporte; el DT invita y el jugador acepta | Verificado |
| RIV-007 | Buscar rivales por cercanía, barrio o ciudad, con rango de distancia | Verificado (cercanía con catálogo sintético) |
| RIV-008 | Retar o publicar búsqueda abierta; ofertas, contraofertas, aceptar, rechazar, retirar, cancelar | Verificado |

## Decisiones

- ADR-006: la cercanía se calcula entre centros de barrio del catálogo; nunca hay coordenadas de personas ni de equipos.
- Árbitro opcional en la búsqueda (con, sin, cualquiera); la oferta debe decidir con o sin.
- Lugar: establecimiento, informal (parque, cancha de barrio) o por acordar.
- Aceptar una oferta deja la búsqueda en "Rival encontrado"; el contrato con firmas llega en el Sprint 3.

## Loop 4 — Verificación (salidas reales del 23/11/2026)

| Verificación | Resultado |
| --- | --- |
| `pytest` en SQLite | 139 aprobadas, 4 omitidas (son las de PostgreSQL) |
| `pytest` en PostgreSQL 16 + PostGIS | 143 aprobadas, incluidas 4 de concurrencia repetidas 3 veces |
| Prueba de humo con servidor real y PostgreSQL | Registro → equipos → rivales → búsqueda → oferta → aceptar → MATCHED |
| `tsc --noEmit` | 0 errores |
| Pruebas de reglas de la app (`npm test`) | 8 aprobadas (edad, fechas en hora de Colombia, rangos) |
| Empaquetado Android | Compila |
| `pip-audit` | Sin vulnerabilidades (se actualizó pytest a 9.0.3 por PYSEC-2026-1845) |
| `npm audit --omit=dev` | Las mismas 3 moderadas del Sprint 1 en herramientas de Expo |
| Líneas por archivo / `any` / `TODO` | Ninguno pasa de 150; sin `any` ni `TODO` |
| App en emulador o teléfono | NO EJECUTADO |

## Revisión independiente

Sin hallazgos ALTO. Confirmó: no se filtran coordenadas, los retos directos solo los ve el retado, invitaciones y solicitudes no se mezclan. Corregido con pruebas:

| Impacto | Problema | Corrección | Prueba |
| --- | --- | --- | --- |
| MEDIO | Se podía ofertar por id a una búsqueda fuera de tu alcance o ciudad | Regla de visibilidad compartida entre feed y oferta | `test_offer_outside_publisher_scope_is_not_found` |
| MEDIO | Aceptar y retirar a la vez dejaba datos inconsistentes | Retirar bloquea la búsqueda igual que aceptar | `test_accept_and_withdraw_at_once_stay_consistent` (PostgreSQL) |
| MEDIO | Se podía ofertar o aceptar una hora pasada | `OFFER_IN_PAST` en dominio y al aceptar; la app propone una hora futura | `test_offer_in_the_past_rejected` |
| MEDIO | El contador del administrador sumaba invitaciones | Solo cuenta solicitudes | `test_admin_counter_ignores_invitations` |
| MEDIO | Un agente libre seguía visible tras unirse por solicitud | Aprobar la solicitud lo desactiva | `test_joining_by_request_removes_free_agent` |
| MEDIO | La app solo mostraba 20 rivales o agentes | "Cargar más" con páginas acumuladas | Revisión de código |
| MEDIO | Doble toque al aceptar una invitación podía dar error 500 | Se relee tras el bloqueo (también en solicitudes) | `test_double_tap_accept_invitation_joins_once` (PostgreSQL) |
| MEDIO | El feed recortaba antes de filtrar y hacía muchas consultas | Filtro por barrio en SQL y conteo agrupado | Pruebas de feed existentes |
| BAJO | La versión de la oferta volvía a 1 tras retirarla | Máximo + 1 por equipo y búsqueda | `test_version_keeps_growing_after_withdraw` |
| BAJO | La app no dejaba ver ni retirar la oferta propia | Botón "Ver mi oferta"; acciones ocultas si la búsqueda cerró | Revisión de código |
| BAJO | Se podía retar a un equipo de otra ciudad | `INVALID_CHALLENGE` | `test_challenge_other_city_rejected` |
| BAJO | Invitaciones sin tope | Máximo 20 pendientes y 7 días de espera tras un rechazo | `test_reinvite_after_rejection_waits_a_week` |

## Defectos y riesgos abiertos

| Impacto | Tema | Plan |
| --- | --- | --- |
| MEDIO | Catálogo real de barrios de Barranquilla pendiente [POR VERIFICAR] | Descargar el "Mapa de Barrios según el POT" de datos.gov.co y convertirlo a centroides |
| MEDIO | Sin migraciones versionadas: la base de desarrollo se recrea | Alembic antes del piloto |
| MEDIO | La app sigue sin pruebas de componentes | jest-expo en el Sprint 3 |
| BAJO | Límites de búsqueda en memoria por proceso | Redis al desplegar con varios procesos |
| BAJO | `/free-agents` lo puede consultar cualquier usuario (dato opcional del jugador, con límite) | Revisar con el abogado los textos de autorización |

## Comandos

```powershell
cd backend; .\venv\Scripts\python.exe -m pytest -q
$env:RIVAL_TEST_DATABASE_URL = "postgresql+psycopg://rival:clave@127.0.0.1/rival_test"; .\venv\Scripts\python.exe -m pytest -q
cd mobile; npm run typecheck; npm test
```
'@
Write-RivalText 'docs\superpowers\plans\2026-11-23-sprint-01-registro-equipos.md' @'
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
'@
Write-RivalText 'docs\superpowers\plans\2026-11-23-sprint-02-rivales-retos.md' @'
# Sprint 2 — Rivales, retos, ofertas y agentes libres — Plan de implementación

> **Para agentes:** usar superpowers:executing-plans. Los pasos usan casillas (`- [ ]`).

**Meta:** un DT encuentra rival por cercanía, barrio o ciudad, lo reta o publica una búsqueda abierta que recibe ofertas al estilo InDriver; los jugadores sin equipo aparecen como agentes libres y aceptan invitaciones.

**Arquitectura:** mismas capas del Sprint 1. Cercanía entre centros de barrio del catálogo (ADR-006). Pruebas en SQLite y PostgreSQL 16 + PostGIS.

**Spec:** documento del Sprint 0, secciones 4.2, 4.3, 4.4.1 y 9.3 (RIV-006, RIV-007, RIV-008).

## Restricciones globales

- Las del Sprint 1, más: nunca coordenadas en respuestas; rangos UNDER_2_KM, FROM_2_TO_5_KM, OVER_5_KM; radio entre 1 y 15 km.
- Fechas con zona horaria (AwareDatetime); la app escribe en hora de Colombia (-05:00).
- Ventana de partido: futura, máximo 14 días de duración, máximo 60 días adelante; máximo 3 búsquedas abiertas por equipo.
- Árbitro opcional: la búsqueda acepta WITH, WITHOUT o EITHER; la oferta debe concretar WITH o WITHOUT.
- Una oferta pendiente por equipo y búsqueda (índice único parcial); una contraoferta crea versión nueva.
- Aceptar bloquea la búsqueda (FOR UPDATE).
- El jugador siempre acepta la invitación; las invitaciones no aparecen como solicitudes del Sprint 1.

## Review Focus

1. Dos administradores aceptan ofertas distintas a la vez: solo una gana (prueba en PostgreSQL).
2. Un reto directo no lo ve ningún equipo distinto del retado.
3. Una búsqueda NEARBY de 2 km no la ve un equipo a 4 km aunque mire "Mi ciudad".
4. Búsqueda vencida: sale del feed y no se puede aceptar ninguna oferta.
5. Fechas sin zona horaria: la API responde 422.

## Tareas

- [x] Dominio: `geo.py`, `match_rules.py` con pruebas.
- [x] Catálogo de barrios: `models_places.py`, `neighborhood_service.py`, `tools/import_neighborhoods.py`.
- [x] Rivales: `rival_service.py`.
- [x] Agentes libres e invitaciones: `free_agent_service.py`, `invitation_service.py`.
- [x] Búsquedas y ofertas: `match_request_service.py`, `match_feed_service.py`, `match_offer_service.py`.
- [x] API: `routes_scouting.py`, `routes_matches.py` con límite de 60 búsquedas por usuario cada 10 minutos.
- [x] App: pantallas de rivales, agentes libres, búsquedas, feed, oferta y ofertas.
- [x] Verificación en SQLite y PostgreSQL, revisión independiente y entrega.
'@
Write-RivalText 'mobile\.gitignore' @'
# Learn more https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files

# dependencies
node_modules/

# Expo
.expo/
dist/
web-build/
expo-env.d.ts

# Native
.kotlin/
*.orig.*
*.jks
*.p8
*.p12
*.key
*.mobileprovision

# Metro
.metro-health-check*

# debug
npm-debug.*
yarn-debug.*
yarn-error.*

# macOS
.DS_Store
*.pem

# local env files
.env*.local

# typescript
*.tsbuildinfo

# generated native folders
/ios
/android
'@
Write-RivalText 'mobile\.prettierrc' @'
{
  "printWidth": 110,
  "singleQuote": true,
  "trailingComma": "all"
}
'@
Write-RivalText 'mobile\App.tsx' @'
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { LoadingScreen, SignedInFlow } from './src/app/SignedInFlow';
import { SignedOutFlow } from './src/app/SignedOutFlow';
import { useNavigator } from './src/controllers/useNavigator';
import { useSession } from './src/controllers/useSession';

function Root() {
  const session = useSession();
  const navigator = useNavigator({ name: 'rolePicker' });
  const { reset } = navigator;

  // Al entrar o salir de sesión, la pila de navegación vuelve a empezar.
  useEffect(() => {
    if (session.status === 'signedIn') reset({ name: 'home' });
    if (session.status === 'signedOut') reset({ name: 'rolePicker' });
  }, [session.status, reset]);

  if (session.status === 'restoring') {
    return <LoadingScreen />;
  }
  if (session.status === 'signedIn' && session.user && session.token) {
    return <SignedInFlow session={session} user={session.user} token={session.token} navigator={navigator} />;
  }
  return <SignedOutFlow session={session} navigator={navigator} />;
}

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar style="dark" />
      <Root />
    </SafeAreaProvider>
  );
}
'@
Write-RivalText 'mobile\README.md' @'
# RIVAL — App móvil

Expo SDK 58 + React Native + TypeScript estricto.

## Capas

- `src/domain`: tipos, validaciones y los 7 estados de vista (`viewState.ts`). Sin React.
- `src/services`: cliente HTTP, API de identidad y equipos, almacenamiento seguro del token.
- `src/controllers`: hooks con el estado y las acciones (`handle*`). Ni HTTP ni SQL en las vistas.
- `src/ui`: componentes y pantallas puras (reciben datos y funciones `on*`).
- `src/app`: composición de pantallas y controladores.

## Conectar con el backend

| Dónde corre la app | Valor de `EXPO_PUBLIC_API_URL` |
| --- | --- |
| Emulador de Android | `http://10.0.2.2:8000` (por defecto; no hay que configurar nada) |
| Teléfono físico en la misma red | `http://<IP-de-tu-PC>:8000` y el backend con `--host 0.0.0.0` |

El modo de teléfono físico expone el backend a tu red local: úsalo solo en una red de confianza y solo para desarrollo.

```powershell
$env:EXPO_PUBLIC_API_URL = "http://192.168.1.50:8000"
npx expo start
```

## Comandos

```powershell
npm ci             # instala exactamente las versiones del package-lock.json
npm run typecheck  # tsc --noEmit
npm test           # pruebas de las reglas locales (edad, fechas, formulario)
npx expo start --android
```

Los iconos de `assets/` son provisionales (una "R" sobre azul).
'@
Write-RivalText 'mobile\app.json' @'
{
  "expo": {
    "name": "RIVAL",
    "slug": "rival",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "ios": {
      "supportsTablet": true
    },
    "android": {
      "adaptiveIcon": {
        "backgroundColor": "#1D4ED8",
        "foregroundImage": "./assets/android-icon-foreground.png",
        "backgroundImage": "./assets/android-icon-background.png",
        "monochromeImage": "./assets/android-icon-monochrome.png"
      },
      "predictiveBackGestureEnabled": false
    },
    "web": {
      "favicon": "./assets/favicon.png"
    }
  }
}
'@
Write-RivalBinary 'mobile\assets\android-icon-background.png' 'iVBORw0KGgoAAAANSUhEUgAABAAAAAQACAYAAAB/HSuDAAAWBklEQVR42u3YQREAMAjAsDEfszT9uAEDKOASCX023s86AAAAwGpXAgAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAJAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwACQAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAkAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAAAAAwAAAAAMAAAAAAAAwAAAAAwAAAAAAADAAAAADAAAAAAAAMAAAAAMAAAAACASQOC0wpCDZFD+wAAAABJRU5ErkJggg=='
Write-RivalBinary 'mobile\assets\android-icon-foreground.png' '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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMDd3v8Aw9R2yXosA54AAAAASUVORK5CYII='
Write-RivalBinary 'mobile\assets\android-icon-monochrome.png' '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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMDd3v8Aw9R2yXosA54AAAAASUVORK5CYII='
Write-RivalBinary 'mobile\assets\favicon.png' 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAB7klEQVR42u3ZPWhTURTA8f+9SRuTxpovK1gsqKCIXRwUty52kEKlFAeRSgZRqFRwkECFDh1LF6dUXbO4FAKCRcRBXES6OaTBYhMlGCFp2iRtXpu8uBpfKKKD7+I547338fi9e8794KkT45k2BofG8BCAAAQgAAEIQAAC+J8B3r95OD4WZv7OwIFjdi2b7brN58Ieq5ld0m+rZHKWOwC/E36fxu/THIt4uTwcYHoySmqlwtzTIi3bwBRSCqauhkjcOmp2DdweD3M4oN2XQtm8xZWZDQAChzSnBntJTMUYudDX+WKP4uI5P29W6+6dgZ2Gzcf1BtMLha75Hg15zUih6o5NaavpaC9vt8wA9PdpYl2+9qcvlruX0Z9rQKvOvtcfauS+7bsPcGbIRz599sAx61/3eJQsmrGR/VoLqZcVkstlKrUWxu0DSoHWUG/YGHmYC/o1dyciLCWOo5RLAdm8xdC1NU5PZhm9v8GLd1XHmNFLQeJjYXfPwH6zzVrO4t5igVfva47+BzeiHAl63J9C7TbMJouOvA8FPcxcj5hRA983mzxLb3a9TwwO9JhRxE+Wy5S2OpfO3h7Fw5sxMwD1hs3j5yVH+8RIP+dP+sxYRlMrFcfxQSmYjf/55UbJHxoBCEAAAhCAAAQgAAH8s/gBIWuRPKw5RjYAAAAASUVORK5CYII='
Write-RivalBinary 'mobile\assets\icon.png' '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AAAAMmtsYz6++omJseAbM2L7LWoNAoAAAACQZXNm1cQtX90ovnLKxKiv8agHgAAAAJBZuVzEB/Zvjnsv2jh2mVNnEAAEAACALJs+sTJ+cv70+NLHJkRttcc+AAEAAIDI8jXAR97TEvdetLF3AwAIAAAAZN2MSZVx41emx4kHtxgDQAAAACDLCvlcfP6ECXH5p6dEQ63HQAABAACATDtw1zGx4J9nxOYzqo0BIAAAAJBlM6dUxe0XbBQH7z7GGAACAAAAWVZbXREXnz0lTnnfWGMACAAAAETGvyXgnA+Pj/NPnhh5T4YAAgAAANn2oQOb44pzpkZttcdDAAEAAIBM23fHhrj+y9OjuSFvDAABAACALJs7uyauO296NIkAAAIAAADZtvXM6rjuS9NEAAABAACArJszqyau+eK0aKz3uAggAAAAkGnbbFoT13xxeoyp88gIIAAAAJBp286uias+MzUqCzljAAgAAABk2c5z6uLrp08yBIAAAABA1h22R2P8/XHjDAEgAAAAkHWnH9UaR+3dZAgAAQAAgKz76qkTY9e31RkCQAAAACDLCvlcXPqpKTGhpWAMAAEAAIAsa23Kx8V/PznyniQBBAAAALJtlzl18XfHeikggAAAAEDmnXpEa7xzu3pDAAgAAABk+kEyF/GtsybHeO8DABAAAACIzL8P4PyTJxgCQAAAACDrDthlTBy46xhDAAgAAABk3fknT4jmhrwhAAQAAACybFxzIb5woo8CAAgAAABk3vve1Rjv2t63AgAIAAAAZN65J06IQj5nCAABAACALJs5pSo+eECzIQAEAAAAsu7M97dGY73HTAABAACATGsZk48zjh5nCAABAACArPvIe5pjo0mVhgAQAAAAyLLKQi7OPtYVAIAAAABA5h28e2PMcAUAIAAAAJBt+YqIUw5vNQSAAAAAQNYduVdjTGotGAJAAAAAIDL+LoCTDx1rCAABAACArDt2v6YY25g3BIAAAABAltVWV8T7920yBIAAAABA1h23X3PkcnYAEAAAAMi06RMr451z6w0BIAAAAJB1x+3fbAQAAQAAgKzbZ4f6mNDiKwEBBAAAADKtkM95GSCAAAAAQAoO27PRCAACAAAAWTdralVsuXG1IQAEAAAAsu69u40xAoAAAABA1r3nHQIAgAAAAEDmzZxSFVtt4mMAAAIAAADhCgAAAQAA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ACAAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAACAAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAACAAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAACAAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAAAgAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAAAgAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAAAgAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAAAgAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAAAAgAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAgAAAAAIAAAAAAAAgAAAAAgAAAAAAACAAAAACAAAAAAAAIAAAAAIAAAAAAAAgAAAAAIACYAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAAEAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAAABAAAAABAAAAAAAAEAAAAABAAAAAAAAEAAAAAEAAAAAAAAQAAAAAQAAAAAIC/uv8HkJuX74jYRhYAAAAASUVORK5CYII='
Write-RivalBinary 'mobile\assets\splash-icon.png' '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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC74H8DrZGGMdorcSMAAAAASUVORK5CYII='
Write-RivalText 'mobile\index.ts' @'
import { registerRootComponent } from 'expo';

import App from './App';

// registerRootComponent calls AppRegistry.registerComponent('main', () => App);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
registerRootComponent(App);
'@
Write-RivalText 'mobile\package-lock.json' @'
{
  "name": "rival-mobile",
  "version": "1.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "rival-mobile",
      "version": "1.0.0",
      "dependencies": {
        "expo": "~58.0.26",
        "expo-secure-store": "~58.0.3",
        "expo-status-bar": "~58.0.5",
        "react": "19.3.0",
        "react-native": "0.88.1",
        "react-native-safe-area-context": "~5.11.1"
      },
      "devDependencies": {
        "@types/node": "^26.6.6",
        "@types/react": "~19.3.0",
        "typescript": "~6.0.3"
      }
    },
    "node_modules/@babel/code-frame": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/code-frame/-/code-frame-7.29.7.tgz",
      "integrity": "sha512-Aup7aUOfpbAUg2ROOJN6Iw5f9DMBlzu0mIkm/malLQFN/YQgO48wCj0Kxa3sEHJvPVFg7siR+qRInwXd2qhQKw==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-validator-identifier": "^7.29.7",
        "js-tokens": "^4.0.0",
        "picocolors": "^1.1.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/compat-data": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/compat-data/-/compat-data-7.29.7.tgz",
      "integrity": "sha512-locTkQyKvwIEgBzVrn8693ebc97F2U8ZHjbXwDXJ5Fn2TCpNwTlKcaKLkdHop5c/icOFE7qt7Q9JC5hnKNa6Gg==",
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/core": {
      "version": "7.29.13",
      "resolved": "https://registry.npmjs.org/@babel/core/-/core-7.29.13.tgz",
      "integrity": "sha512-j1nvOQCZYSgp7HLmisnCXFTpVvFODiijQ9QHkORfGKWH6YDtskTEeCJS7eV545GZ9UBzrq0e2xsOd5QQ5PjIqw==",
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.29.7",
        "@babel/generator": "^7.29.13",
        "@babel/helper-compilation-targets": "^7.29.13",
        "@babel/helper-module-transforms": "^7.29.13",
        "@babel/helpers": "^7.29.13",
        "@babel/parser": "^7.29.13",
        "@babel/template": "^7.29.7",
        "@babel/traverse": "^7.29.13",
        "@babel/types": "^7.29.11",
        "@jridgewell/remapping": "^2.3.5",
        "convert-source-map": "^2.0.0",
        "debug": "^4.1.0",
        "gensync": "^1.0.0-beta.2",
        "json5": "^2.2.3",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/babel"
      }
    },
    "node_modules/@babel/core/node_modules/semver": {
      "version": "6.3.2",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.2.tgz",
      "integrity": "sha512-GYrCADwpu6yV5OAvchkQ27Z5wwMxWAEMg5NNWjyHh/5DboFFqbdbvYNIvZouQpxXyeMPoTOh0vdPYKlf0ZswdQ==",
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/@babel/generator": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/generator/-/generator-7.29.15.tgz",
      "integrity": "sha512-gNWJUX0FlevflramOkaInywOMhU1lkln38gAC7TFZv2tsWbLYbN/2WZFGcq8zbX0Z55e4vGa27IB/NaeZoauWQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/parser": "^7.29.15",
        "@babel/types": "^7.29.15",
        "@jridgewell/gen-mapping": "^0.3.12",
        "@jridgewell/trace-mapping": "^0.3.28",
        "jsesc": "^3.0.2"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-annotate-as-pure": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-annotate-as-pure/-/helper-annotate-as-pure-7.29.7.tgz",
      "integrity": "sha512-OoK6239jHPuSQOoS0kfTVKn0b/rVTk0seKq4Gd2UMLtmOVLjDC0ki3e+c90Trqv2gMfvJFqkiljrr568+qddiw==",
      "license": "MIT",
      "dependencies": {
        "@babel/types": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-compilation-targets": {
      "version": "7.29.13",
      "resolved": "https://registry.npmjs.org/@babel/helper-compilation-targets/-/helper-compilation-targets-7.29.13.tgz",
      "integrity": "sha512-8WxJ4/Vmes3ghacj8VOJy3NW8eyHiFY/4thU/LSBuBE470+igjR/j1ZTNn8fV5VdNrLx6iXUwig526UdOvfP0w==",
      "license": "MIT",
      "dependencies": {
        "@babel/compat-data": "^7.29.7",
        "@babel/helper-validator-option": "^7.29.7",
        "browserslist": "^4.24.0",
        "lru-cache": "^5.1.1",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-compilation-targets/node_modules/semver": {
      "version": "6.3.2",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.2.tgz",
      "integrity": "sha512-GYrCADwpu6yV5OAvchkQ27Z5wwMxWAEMg5NNWjyHh/5DboFFqbdbvYNIvZouQpxXyeMPoTOh0vdPYKlf0ZswdQ==",
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/@babel/helper-create-class-features-plugin": {
      "version": "7.29.13",
      "resolved": "https://registry.npmjs.org/@babel/helper-create-class-features-plugin/-/helper-create-class-features-plugin-7.29.13.tgz",
      "integrity": "sha512-fo8/Fr44/DMV71FQjk/HA0Npmu3bo5DFoWTCW1dhUR8Vx3NFfAVeEy0TbcBpt4e+hd2QhdmWgmspHo/9iWj8RA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-annotate-as-pure": "^7.29.7",
        "@babel/helper-member-expression-to-functions": "^7.29.7",
        "@babel/helper-optimise-call-expression": "^7.29.7",
        "@babel/helper-replace-supers": "^7.29.7",
        "@babel/helper-skip-transparent-expression-wrappers": "^7.29.13",
        "@babel/traverse": "^7.29.13",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0"
      }
    },
    "node_modules/@babel/helper-create-class-features-plugin/node_modules/semver": {
      "version": "6.3.2",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.2.tgz",
      "integrity": "sha512-GYrCADwpu6yV5OAvchkQ27Z5wwMxWAEMg5NNWjyHh/5DboFFqbdbvYNIvZouQpxXyeMPoTOh0vdPYKlf0ZswdQ==",
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/@babel/helper-create-regexp-features-plugin": {
      "version": "7.29.14",
      "resolved": "https://registry.npmjs.org/@babel/helper-create-regexp-features-plugin/-/helper-create-regexp-features-plugin-7.29.14.tgz",
      "integrity": "sha512-nKvzhuLMMnFHHsENpUZh4N2e+LqnKDgT0SMibSyv8aW8FqGKWMqLO/zdnRjAYcruH9At6LVicWg7DgTc6IPzNg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-annotate-as-pure": "^7.29.7",
        "regexpu-core": "^6.5.4",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0"
      }
    },
    "node_modules/@babel/helper-create-regexp-features-plugin/node_modules/semver": {
      "version": "6.3.2",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.2.tgz",
      "integrity": "sha512-GYrCADwpu6yV5OAvchkQ27Z5wwMxWAEMg5NNWjyHh/5DboFFqbdbvYNIvZouQpxXyeMPoTOh0vdPYKlf0ZswdQ==",
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/@babel/helper-define-polyfill-provider": {
      "version": "0.6.8",
      "resolved": "https://registry.npmjs.org/@babel/helper-define-polyfill-provider/-/helper-define-polyfill-provider-0.6.8.tgz",
      "integrity": "sha512-47UwBLPpQi1NoWzLuHNjRoHlYXMwIJoBf7MFou6viC/sIHWYygpvr0B6IAyh5sBdA2nr2LPIRww8lfaUVQINBA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-compilation-targets": "^7.28.6",
        "@babel/helper-plugin-utils": "^7.28.6",
        "debug": "^4.4.3",
        "lodash.debounce": "^4.0.8",
        "resolve": "^1.22.11"
      },
      "peerDependencies": {
        "@babel/core": "^7.4.0 || ^8.0.0-0 <8.0.0"
      }
    },
    "node_modules/@babel/helper-globals": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-globals/-/helper-globals-7.29.7.tgz",
      "integrity": "sha512-3nQVUAtvkKH9zahfWgw96Jc/uFOmjACE1kQz82E2lqWmHBgjzbNlsC22nuQTfahmWeQtTq5nQ/4Nnd2A1wj4zA==",
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-member-expression-to-functions": {
      "version": "7.29.14",
      "resolved": "https://registry.npmjs.org/@babel/helper-member-expression-to-functions/-/helper-member-expression-to-functions-7.29.14.tgz",
      "integrity": "sha512-FuTSn8mXKAP+aHXnbkCYQsQAdlEIJptEutwc2NaPd28hyVqsjRDmBnI2EPJX6HCodKIqOHfayQHqtxQCkqwthA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-skip-transparent-expression-wrappers": "^7.29.13",
        "@babel/traverse": "^7.29.14",
        "@babel/types": "^7.29.14"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-module-imports": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-module-imports/-/helper-module-imports-7.29.7.tgz",
      "integrity": "sha512-ejHwrQQYcm9xnTivShn2IDOlIzInN34AXskvq9QicvCtEzq1Vzclu/tKF8Jq1Cg8JG2GL6/EmjgsCT7lXepE3g==",
      "license": "MIT",
      "dependencies": {
        "@babel/traverse": "^7.29.7",
        "@babel/types": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-module-transforms": {
      "version": "7.29.14",
      "resolved": "https://registry.npmjs.org/@babel/helper-module-transforms/-/helper-module-transforms-7.29.14.tgz",
      "integrity": "sha512-2XDvQVd9JESaOgGc4jT2/jquTAO7ppA5noTZQqH+MmZ89yjCzScLwtCPbWtkPZylL+TLWR49IwWmk+QkRR4GsA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-module-imports": "^7.29.7",
        "@babel/helper-validator-identifier": "^7.29.7",
        "@babel/traverse": "^7.29.14"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0"
      }
    },
    "node_modules/@babel/helper-optimise-call-expression": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-optimise-call-expression/-/helper-optimise-call-expression-7.29.7.tgz",
      "integrity": "sha512-+kmGVjcT9RGYzoDwdwEqEvGgKe3BYq+O1iGzjFubaNgZHwYHP6lsF2Yghf4kEuv9BV7tYDZ913aBW9am6YKong==",
      "license": "MIT",
      "dependencies": {
        "@babel/types": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-plugin-utils": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-plugin-utils/-/helper-plugin-utils-7.29.7.tgz",
      "integrity": "sha512-G7sHYigPY17oO5SYWnfD/0MTBwVR781S/JI643e/JhUYgVgWE/61SoW3NH9KWUKyKq5LVh3npif99Wkt6j86Jw==",
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-remap-async-to-generator": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-remap-async-to-generator/-/helper-remap-async-to-generator-7.29.7.tgz",
      "integrity": "sha512-16AMiW26DbXWBbr3B8wNozKM0ydMLB892vaOaJW/fPJdnT8vJk5sdkQcU/isqUxyCE0cEoa8wZOcbgDuC4b6Og==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-annotate-as-pure": "^7.29.7",
        "@babel/helper-wrap-function": "^7.29.7",
        "@babel/traverse": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0"
      }
    },
    "node_modules/@babel/helper-replace-supers": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-replace-supers/-/helper-replace-supers-7.29.7.tgz",
      "integrity": "sha512-atfGXWSeCiF4DnKZIfmJfQRkSw9b9gNNXR1kqKjbhG4pGYCOnkp8OcTB8E3NXjBu8NpheSnOeNKz8KT7UNFTmQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-member-expression-to-functions": "^7.29.7",
        "@babel/helper-optimise-call-expression": "^7.29.7",
        "@babel/traverse": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0"
      }
    },
    "node_modules/@babel/helper-skip-transparent-expression-wrappers": {
      "version": "7.29.13",
      "resolved": "https://registry.npmjs.org/@babel/helper-skip-transparent-expression-wrappers/-/helper-skip-transparent-expression-wrappers-7.29.13.tgz",
      "integrity": "sha512-Abm4rKIH0tmCayJLwcoeOkdzpYUphTbO52fHhyEBHn7S0R+ni4epNLI/8nq1L0DN2Bl0u5qmgWm2Og/z4fBb+Q==",
      "license": "MIT",
      "dependencies": {
        "@babel/traverse": "^7.29.13",
        "@babel/types": "^7.29.11"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-string-parser": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/helper-string-parser/-/helper-string-parser-7.29.15.tgz",
      "integrity": "sha512-C2FuapQ2Kh1OnVHAoLi5rD3GBJ8COb9Q609T6HEpLqaBAo560PDP5OxBE5dCI/h951MBO/+bCUYU5SZ+8ZlV+w==",
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-validator-identifier": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-validator-identifier/-/helper-validator-identifier-7.29.7.tgz",
      "integrity": "sha512-qehxGkRj55h/ff8EMaJ+cYhyaKlHIxqYDn682wQD7RNp9UujOQsHog2uS0r2vzr4pW+sXf90NeeayjcNaX3fFg==",
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-validator-option": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-validator-option/-/helper-validator-option-7.29.7.tgz",
      "integrity": "sha512-N9ZErrD+yW5geCDtBqnOoxmR8+tNKiGuxKlDpuJxfsqpa2dFcexaziGAE/qoHLiDDreVNMupxGmSoNlyvsA3gw==",
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-wrap-function": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/helper-wrap-function/-/helper-wrap-function-7.29.15.tgz",
      "integrity": "sha512-14dKROQSpuNYPw+4wpADe87YLS1VnP/ua3gKTRpEAX1ErBayLMgK/KpWbCP/uYiCSBAVGp/a7bY8MqRfFNRqOQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/template": "^7.29.7",
        "@babel/traverse": "^7.29.15",
        "@babel/types": "^7.29.15"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helpers": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/helpers/-/helpers-7.29.15.tgz",
      "integrity": "sha512-l+ezV2czw3t2d2ELq+3CwPL4WLKK5O8IywBXb9/gpmbCOVZFmRYJPmHVqSCv2k+8iKbE30Zf54siOoIZ52XOxA==",
      "license": "MIT",
      "dependencies": {
        "@babel/template": "^7.29.7",
        "@babel/types": "^7.29.15"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/parser": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/parser/-/parser-7.29.15.tgz",
      "integrity": "sha512-RpKWyisHoP81twtSCgmE02iU0RnPcq1DN5bBEbpUePrjA9Q3wXhufnCJrrayPpoZieqFh3zyZQqwtSK0gGccRA==",
      "license": "MIT",
      "dependencies": {
        "@babel/types": "^7.29.15"
      },
      "bin": {
        "parser": "bin/babel-parser.js"
      },
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@babel/plugin-proposal-decorators": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-proposal-decorators/-/plugin-proposal-decorators-7.29.7.tgz",
      "integrity": "sha512-EtU0Hi3GvrTqD56xKmZvV/uCXK2ZbwVNPNLAquVItcAZpUhkXwWlo3Fmj0c2LxgSf2I8IDULeAepwNP1OefLXg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-create-class-features-plugin": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/plugin-syntax-decorators": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-proposal-export-default-from": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/plugin-proposal-export-default-from/-/plugin-proposal-export-default-from-7.29.15.tgz",
      "integrity": "sha512-G9TJJ6ZTxhCGuFlYXB2W8ljMXhkaR2nZEV1DVetC0LgwaibQSVBHq2gD4ldxsfT4/vSzy/V2ARtCmGz1NUlSZg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-syntax-decorators": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-syntax-decorators/-/plugin-syntax-decorators-7.29.7.tgz",
      "integrity": "sha512-9MTTLbF39X6sqM92JPEsoI7++26hjZvzkxKZy64aMhWLH2mPkJ/Q3AV4QLmls3R14FpSpkOwQQfUh962JGQxxg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-syntax-dynamic-import": {
      "version": "7.8.3",
      "resolved": "https://registry.npmjs.org/@babel/plugin-syntax-dynamic-import/-/plugin-syntax-dynamic-import-7.8.3.tgz",
      "integrity": "sha512-5gdGbFon+PszYzqs83S3E5mpi7/y/8M9eC90MRTZfduQOYW76ig6SOSPNe41IG5LoP3FGBn2N0RjVDSQiS94kQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.8.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-syntax-export-default-from": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-syntax-export-default-from/-/plugin-syntax-export-default-from-7.29.7.tgz",
      "integrity": "sha512-foag0BB37ROhdeIX9O8G0jX7hw0UekJc04cHMrYLOnrErsnBKqJGHJ8eDRpoCFZBvEPPygmmtw4qyU97qa4oOw==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-syntax-flow": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-syntax-flow/-/plugin-syntax-flow-7.29.7.tgz",
      "integrity": "sha512-ajMX6QPcyomotqwpzhkYGxcK2i/us0rs1Qo9QvUpa+Fca0FTmqrzKrctoIYLMxcOhGZldGT/BAVkRGTWBiR8gQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-syntax-jsx": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-syntax-jsx/-/plugin-syntax-jsx-7.29.7.tgz",
      "integrity": "sha512-TSu8+mHCoEaaCDEZ0I3+6mvTBYR4PCxQwf2z9/r5Tbztv6NaLR3B9thGTTxX2WGuGHJqRiAbKPeGTJ5XWXVg6A==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-syntax-nullish-coalescing-operator": {
      "version": "7.8.3",
      "resolved": "https://registry.npmjs.org/@babel/plugin-syntax-nullish-coalescing-operator/-/plugin-syntax-nullish-coalescing-operator-7.8.3.tgz",
      "integrity": "sha512-aSff4zPII1u2QD7y+F8oDsz19ew4IGEJg9SVW+bqwpwtfFleiQDMdzA/R+UlWDzfnHFCxxleFT0PMIrR36XLNQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.8.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-syntax-optional-chaining": {
      "version": "7.8.3",
      "resolved": "https://registry.npmjs.org/@babel/plugin-syntax-optional-chaining/-/plugin-syntax-optional-chaining-7.8.3.tgz",
      "integrity": "sha512-KoK9ErH1MBlCPxV0VANkXW2/dw4vlbGDrFgz8bmUsBGYkFRcbRwMh6cIJubdPrkxRwuGdtCk0v/wPTKbQgBjkg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.8.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-syntax-typescript": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-syntax-typescript/-/plugin-syntax-typescript-7.29.7.tgz",
      "integrity": "sha512-ngr+82Sh0xMz25TPCZi+nC2iTzjfCdWS2ONXTp/PtSCHCgaCNBpdMqgvJ2ccdLlClVZ7sisIgB914j/JFe+RZA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-async-generator-functions": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-async-generator-functions/-/plugin-transform-async-generator-functions-7.29.7.tgz",
      "integrity": "sha512-d98gXZkgswvkyohMBABkhm3GeXhYj8psWfwQ2C7gtfrKGTykQa/iOIi+JJhwMjPlZ6Vm2XN+DCf3Es1EoG4ZLA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/helper-remap-async-to-generator": "^7.29.7",
        "@babel/traverse": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-async-to-generator": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-async-to-generator/-/plugin-transform-async-to-generator-7.29.7.tgz",
      "integrity": "sha512-pcUb2SS+RMo9TWVBwKGI5ShtoG7R+zBsFmCKDa6fe8c+hPr3XJlZgoE5j6i8W7gDjhyvy+85vmYexanvXh3d1w==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-module-imports": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/helper-remap-async-to-generator": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-block-scoping": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-block-scoping/-/plugin-transform-block-scoping-7.29.15.tgz",
      "integrity": "sha512-jfJWMNOYxJUQ3VMdMF0KpmPaugSKRbwLYqxM8UHOga7jKnlbhe18yhBKwiAkaOWrxmxesONjAhtEqTyn2rB2qg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-class-properties": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-class-properties/-/plugin-transform-class-properties-7.29.7.tgz",
      "integrity": "sha512-GtcpjFvanPfzNQi3eTitsCqtRRmmqzpy/A+yhTR1HaZo1Ly3EA8ZXxlPyHdR8/IuRMYc3E4wdGBewB2QKQjAaA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-create-class-features-plugin": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-class-static-block": {
      "version": "7.29.14",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-class-static-block/-/plugin-transform-class-static-block-7.29.14.tgz",
      "integrity": "sha512-4rr6WKSu9DzMYpcTlbjHw6hFRk0Gkys3D54mqNE4tOyYQFOTrf3RBhntYH62ec/fbvgGEVATh5cqGZjM2Yc3gw==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-create-class-features-plugin": "^7.29.13",
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.12.0"
      }
    },
    "node_modules/@babel/plugin-transform-classes": {
      "version": "7.29.11",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-classes/-/plugin-transform-classes-7.29.11.tgz",
      "integrity": "sha512-f8kTDM/nTvpLeafb+TJ4jboFr/Y3BbC+QzgPpPGzSKJqWLnj9LW0WLqv4XKA11LX5sr+EgvLE6Ix3YsCEusodw==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-annotate-as-pure": "^7.29.7",
        "@babel/helper-compilation-targets": "^7.29.7",
        "@babel/helper-globals": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/helper-replace-supers": "^7.29.7",
        "@babel/traverse": "^7.29.10"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-destructuring": {
      "version": "7.29.13",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-destructuring/-/plugin-transform-destructuring-7.29.13.tgz",
      "integrity": "sha512-X2meXB39NOPPmmshSRJzyd50hX9uCzbscNQwVCjLCtq363PZIJFFxJIeZPpgAewC570vpdeGIHTcltwd0QUlJg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/traverse": "^7.29.13"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-export-namespace-from": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-export-namespace-from/-/plugin-transform-export-namespace-from-7.29.15.tgz",
      "integrity": "sha512-wUo8dEPcDN/gO5/ZoNLDcAFqbJ//idBuMpprfa7NAZ6+Y3PRShTNLcgnKnBAW6vnEDMHiPDwDi62mM90qz7mcQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-flow-strip-types": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-flow-strip-types/-/plugin-transform-flow-strip-types-7.29.7.tgz",
      "integrity": "sha512-wRHeUjUjCZnMHmiO5bRgjFLcoEh7JyTdByOW11ahhwNa4V0bmeGEaIvt51yq0zQp2yWIpqfxXXPyUP6GFJZHOQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/plugin-syntax-flow": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-for-of": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-for-of/-/plugin-transform-for-of-7.29.15.tgz",
      "integrity": "sha512-JHa0QfVEG23goXwV1j8HT31EEIZ8nUJBKNTJ/UU1AwfRqY+7xXBEg9M61Tbz60sxKomE2MQBA3vovEbplL964Q==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/helper-skip-transparent-expression-wrappers": "^7.29.13"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-logical-assignment-operators": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-logical-assignment-operators/-/plugin-transform-logical-assignment-operators-7.29.7.tgz",
      "integrity": "sha512-A0H91hh6W8MFRkp5TqJmMr39jzGD1A1E1Ysiv2O06Sfbhkapm+XyIzxWCEh5kqwOZ1/8QZ0dY3SeQ7XBqfJd5Q==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-modules-commonjs": {
      "version": "7.29.14",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-modules-commonjs/-/plugin-transform-modules-commonjs-7.29.14.tgz",
      "integrity": "sha512-mbv2yy5dqP6e3DbusCx+5AypXkFbyJD/JhG4/XhA+BIADOw5o7W+X0ewSp/h3w7gRL3oR5yny2/K8ljiydj4uA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-module-transforms": "^7.29.14",
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-named-capturing-groups-regex": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-named-capturing-groups-regex/-/plugin-transform-named-capturing-groups-regex-7.29.7.tgz",
      "integrity": "sha512-vuFoLwr4qnv2xbZ16SQd6uPcH5FNrLHhk/Jzo++0XJFcaDsr4gjJVg6j398oMHiC+83k/GiBzviwF5KBJkPUtQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-create-regexp-features-plugin": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0"
      }
    },
    "node_modules/@babel/plugin-transform-nullish-coalescing-operator": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-nullish-coalescing-operator/-/plugin-transform-nullish-coalescing-operator-7.29.7.tgz",
      "integrity": "sha512-idmp1dFaekP9GbcMvG24Kvw2BfhFZjHnNJCkV4WuIY4PskJzwI3f1N5OdgYke38T7rftO6ERulFRn2cFeZwRkg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-object-rest-spread": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-object-rest-spread/-/plugin-transform-object-rest-spread-7.29.7.tgz",
      "integrity": "sha512-Ld98jn4c0smUywL57m7SgsHq3OpThOa6LqZJif3G6jYOovPleoFhVrBJ1WegRApSFB2wu4+RelAj9AC9G08Z4A==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-compilation-targets": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/plugin-transform-destructuring": "^7.29.7",
        "@babel/plugin-transform-parameters": "^7.29.7",
        "@babel/traverse": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-optional-catch-binding": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-optional-catch-binding/-/plugin-transform-optional-catch-binding-7.29.7.tgz",
      "integrity": "sha512-sLsyndxK2VwX6yNUOakMb7Sh553ZTe/vVM1XJ+9Z5aW1ytsc8xOIwmyk05NNjN60vkc5/KqoTH6hB4V41LJhng==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-optional-chaining": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-optional-chaining/-/plugin-transform-optional-chaining-7.29.7.tgz",
      "integrity": "sha512-6GM1dhvK3gNODkXcEcMCOLEDCLSoZ/sBbro2Ax8HURyasQ4NshagQixkRFdh5niI6E4gmA/jYI/4aT7rRos3ZQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/helper-skip-transparent-expression-wrappers": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-parameters": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-parameters/-/plugin-transform-parameters-7.29.7.tgz",
      "integrity": "sha512-ZDOBqV/qLYJI0YElr8DcENEyARsFQeESqWXH6gZlghYXuPPjvweuDhP4VyEi4BlUBlLRFZVjxoZDMjxhLW766g==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-private-methods": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-private-methods/-/plugin-transform-private-methods-7.29.7.tgz",
      "integrity": "sha512-/6Rz4DK1ETDEM/bWHsPHcaEe7ZaT1EqSXjtSP/L0DijOYuaUhiRiOKcwpZ8P7zR4xXEHc2ITdiCgBm9Tpyv9ug==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-create-class-features-plugin": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-private-property-in-object": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-private-property-in-object/-/plugin-transform-private-property-in-object-7.29.7.tgz",
      "integrity": "sha512-+BNo06dnrzdNNqCm1X6YUaVv0DKk8Q+JYcoZfOkLhYWNCXzlwTSRq8zGWayT1csjcpNXV9CQTBRRbmTLZac5cA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-annotate-as-pure": "^7.29.7",
        "@babel/helper-create-class-features-plugin": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-react-display-name": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-react-display-name/-/plugin-transform-react-display-name-7.29.7.tgz",
      "integrity": "sha512-+1wdDMGNb4UPeY3Q4L5yLiYe6TXPXubs4NjrgRFw13hPRLJfEMw2Q5OXkee6/IfdqePIeW4Jjwe3aBh7SdKz4Q==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-react-jsx": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-react-jsx/-/plugin-transform-react-jsx-7.29.7.tgz",
      "integrity": "sha512-WsZulLVBUHXVj2cUcPVx6UE21TpalB6bHbSFErKT0Ib++ax24jjXe73FqlWvdylFOjiuPHYi6VCcgRad1ItN+A==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-annotate-as-pure": "^7.29.7",
        "@babel/helper-module-imports": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/plugin-syntax-jsx": "^7.29.7",
        "@babel/types": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-react-jsx-development": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-react-jsx-development/-/plugin-transform-react-jsx-development-7.29.7.tgz",
      "integrity": "sha512-Xfy3UVMF04+ypnFbkhvfqtmvwfe92qwQdbGZVonhE+6v35GzlofmOnA1szaZqzb9xYWr0nl1e5EMmzi0DNON1g==",
      "license": "MIT",
      "dependencies": {
        "@babel/plugin-transform-react-jsx": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-react-pure-annotations": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-react-pure-annotations/-/plugin-transform-react-pure-annotations-7.29.7.tgz",
      "integrity": "sha512-H5E+HBgDpr6Q5t+Aj11tL7XkIui1jhbIoArVQnqjgXo5/3YxkN7ZEBcWF4RQlB0T4rrxJQbXS6kiFV6B7XTqUA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-annotate-as-pure": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-runtime": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-runtime/-/plugin-transform-runtime-7.29.7.tgz",
      "integrity": "sha512-xmAscdE/AsqRW7vutbPNoUmu/nF5SrLKPs7aoJgEjo35lLKA/Bc0i2rMv/hr1+Y0o1bQCiVtith3u2vdgRL39Q==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-module-imports": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7",
        "babel-plugin-polyfill-corejs2": "^0.4.14",
        "babel-plugin-polyfill-corejs3": "^0.13.0",
        "babel-plugin-polyfill-regenerator": "^0.6.5",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-runtime/node_modules/semver": {
      "version": "6.3.2",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.2.tgz",
      "integrity": "sha512-GYrCADwpu6yV5OAvchkQ27Z5wwMxWAEMg5NNWjyHh/5DboFFqbdbvYNIvZouQpxXyeMPoTOh0vdPYKlf0ZswdQ==",
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/@babel/plugin-transform-typescript": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-typescript/-/plugin-transform-typescript-7.29.15.tgz",
      "integrity": "sha512-FFuMssbHj8DFMDsTH8xrgKBiE1eXuDvO9jLqav7/vsIe6YdoyPQbWCgLNzQxkcIkOv5itBD17TvZkHGIjUMzLg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-annotate-as-pure": "^7.29.7",
        "@babel/helper-create-class-features-plugin": "^7.29.13",
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/helper-skip-transparent-expression-wrappers": "^7.29.13",
        "@babel/plugin-syntax-typescript": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/plugin-transform-unicode-regex": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/plugin-transform-unicode-regex/-/plugin-transform-unicode-regex-7.29.7.tgz",
      "integrity": "sha512-7D/x/23/d/3VqZ0QA+LGbZMlGwZjztBygSWWWsfTPoQ1oQ6Q1P6Mr3d0kk42XabyUVw+fha3LqdRsFqeKqvCyA==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-create-regexp-features-plugin": "^7.29.7",
        "@babel/helper-plugin-utils": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/preset-typescript": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/preset-typescript/-/preset-typescript-7.29.7.tgz",
      "integrity": "sha512-/Foi8vKY2EVbed/1eZx0gJEEwHAIxogrySI7rULcRIvhZzbvoE/b5qG5Ghc0WKAFKOHA9SD1x7RsFlOYdutIiQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-plugin-utils": "^7.29.7",
        "@babel/helper-validator-option": "^7.29.7",
        "@babel/plugin-syntax-jsx": "^7.29.7",
        "@babel/plugin-transform-modules-commonjs": "^7.29.7",
        "@babel/plugin-transform-typescript": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0-0"
      }
    },
    "node_modules/@babel/runtime": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/runtime/-/runtime-7.29.15.tgz",
      "integrity": "sha512-304gsbbGVmQc+cNGHzwHBlqepYdWLKj3VXCQBGt/EGcV7PUPfKI7kAUNW1FZEOCwlQiLvQjg1JEaAlRQ616h+Q==",
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/template": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/template/-/template-7.29.7.tgz",
      "integrity": "sha512-puq+Gf35oI24FeN11LkoUQFqv9uwNeWpxXZi/Ji3rRIoKAzKnxRaZ+Gkj0vKS9ZCiTESfng1N9LyOyXvo+m+Gg==",
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.29.7",
        "@babel/parser": "^7.29.7",
        "@babel/types": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/traverse": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/traverse/-/traverse-7.29.15.tgz",
      "integrity": "sha512-ZfawBo2i8vvt+BTt37dWDKBPjUfm/H+bw+ltwsCRhW7gPtyNVwUXuNo54eO2Xo+P4VXpalPFfFISbBTRKC8SOQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.29.7",
        "@babel/generator": "^7.29.15",
        "@babel/helper-globals": "^7.29.7",
        "@babel/parser": "^7.29.15",
        "@babel/template": "^7.29.7",
        "@babel/types": "^7.29.15",
        "debug": "^4.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/types": {
      "version": "7.29.15",
      "resolved": "https://registry.npmjs.org/@babel/types/-/types-7.29.15.tgz",
      "integrity": "sha512-/XKpKDakL//LZ66bq1XsZOswuqeI5MZqPLDu18o3XdkU1fNJ7bdPtzgnc4ZNS+bBGHV0FJG8jjb8SwcC3nNVQQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-string-parser": "^7.29.15",
        "@babel/helper-validator-identifier": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@expo/code-signing-certificates": {
      "version": "0.0.7",
      "resolved": "https://registry.npmjs.org/@expo/code-signing-certificates/-/code-signing-certificates-0.0.7.tgz",
      "integrity": "sha512-zP0tnfqrFFRL8INtOaQ6XwEYfdIpIH9vrEo7y0bHQGQa50z4/QWXE5CI4nRUHxqFW4MVWOwXFg1hom1aAZHNkQ==",
      "license": "MIT",
      "dependencies": {
        "node-forge": "^1.4.0"
      },
      "engines": {
        "node": ">=22.13.0"
      }
    },
    "node_modules/@expo/config": {
      "version": "58.0.12",
      "resolved": "https://registry.npmjs.org/@expo/config/-/config-58.0.12.tgz",
      "integrity": "sha512-Ch/4Cb8womWYpY1zI4BEEYT1rGuKti8O8aSzyAM79xNTVRx6nPw2h9j91Knq95OSH3wtjrcthZwVYZ3po4igNg==",
      "license": "MIT",
      "dependencies": {
        "@expo/config-plugins": "~58.0.13",
        "@expo/config-types": "^58.0.3",
        "@expo/json-file": "^11.2.1",
        "@expo/platforms": "^58.0.1",
        "@expo/require-utils": "^58.0.6",
        "resolve-workspace-root": "^2.0.0",
        "semver": "^7.7.4",
        "slugify": "^1.3.4"
      }
    },
    "node_modules/@expo/config-plugins": {
      "version": "58.0.13",
      "resolved": "https://registry.npmjs.org/@expo/config-plugins/-/config-plugins-58.0.13.tgz",
      "integrity": "sha512-Vbkt0vpIJ9z+oCFr2simtfuiPxdpIovDgYnzenC9z7jX0rlo8nTLGQky+q+SJdovIbyymGAO45UR0YqwLgbvKw==",
      "license": "MIT",
      "dependencies": {
        "@expo/config-types": "^58.0.3",
        "@expo/json-file": "~11.2.1",
        "@expo/plist": "^0.10.2",
        "@expo/require-utils": "^58.0.6",
        "@expo/sdk-runtime-versions": "^1.0.1",
        "chalk": "^4.1.2",
        "debug": "^4.3.5",
        "semver": "^7.7.4",
        "slugify": "^1.6.6",
        "tinyglobby": "^0.2.15",
        "xcode": "^4.0.0",
        "xml2js": "0.6.0"
      }
    },
    "node_modules/@expo/config-types": {
      "version": "58.0.3",
      "resolved": "https://registry.npmjs.org/@expo/config-types/-/config-types-58.0.3.tgz",
      "integrity": "sha512-wyfrwkTT/hQHzwyqkXkngKxoOa8L6ovsTP4h/UukS1mTmssee5et6HOPoN5RtawdJPnm5JO28f//C/wXlpka8Q==",
      "license": "MIT"
    },
    "node_modules/@expo/devcert": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/@expo/devcert/-/devcert-1.2.2.tgz",
      "integrity": "sha512-wz1YedXwdNbYqk/PRr34vixnuw1+l6uSwmPXUj649cot5iYNccb2zIOnK7Nonb1Pfd/dxAY6CvU6KM3uSdxC7A==",
      "license": "MIT",
      "dependencies": {
        "@expo/sudo-prompt": "^9.3.1",
        "debug": "^3.1.0"
      }
    },
    "node_modules/@expo/devcert/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/@expo/env": {
      "version": "2.6.0",
      "resolved": "https://registry.npmjs.org/@expo/env/-/env-2.6.0.tgz",
      "integrity": "sha512-pSNESQU0IGhLs/A3QlNPoh/acb1vWU7N721OjaIm3JT8yzgZymIM/m4x2y73YwpEtqgwWsCl6+japtq2PtXIPw==",
      "license": "MIT",
      "dependencies": {
        "chalk": "^4.0.0",
        "debug": "^4.3.4"
      },
      "engines": {
        "node": ">=20.12.0"
      }
    },
    "node_modules/@expo/fingerprint": {
      "version": "0.21.10",
      "resolved": "https://registry.npmjs.org/@expo/fingerprint/-/fingerprint-0.21.10.tgz",
      "integrity": "sha512-u73rWDHOYijO1wT60uKjtuoGBKsU9/MFSh7WEE63K2jJ0ML8eycUCXF9FmLf3EVzzIjYIPu6Ns04LR7FVGh6mA==",
      "license": "MIT",
      "dependencies": {
        "@expo/env": "^2.6.0",
        "@expo/spawn-async": "^1.8.0",
        "arg": "^5.0.2",
        "chalk": "^4.1.2",
        "debug": "^4.3.4",
        "ignore": "^5.3.1",
        "minimatch": "^10.2.6",
        "resolve-from": "^5.0.0",
        "semver": "^7.7.4"
      },
      "bin": {
        "fingerprint": "bin/cli.js"
      }
    },
    "node_modules/@expo/image-utils": {
      "version": "0.12.7",
      "resolved": "https://registry.npmjs.org/@expo/image-utils/-/image-utils-0.12.7.tgz",
      "integrity": "sha512-fuiRQxvvkbj932BamtYh1UKuyRJ5tXBJ3XxpGm5pT4zzynPmygd3RtOQrzIhcsIZGcG6i1n+KvrszYRnk3evqQ==",
      "license": "MIT",
      "dependencies": {
        "@expo/require-utils": "^58.0.6",
        "@expo/spawn-async": "^1.8.0",
        "chalk": "^4.0.0",
        "jimp-compact": "0.16.1",
        "parse-png": "^2.1.0",
        "semver": "^7.7.4"
      }
    },
    "node_modules/@expo/inline-modules": {
      "version": "0.2.10",
      "resolved": "https://registry.npmjs.org/@expo/inline-modules/-/inline-modules-0.2.10.tgz",
      "integrity": "sha512-WFqhlOrUUc0VZxrUPq5X328aP2e/cQKvJJXhwNxNj9fqWS9iFWC1E9VRHHhJIqdu+qy2YU3s2OBDlyIz9X/5aA==",
      "license": "MIT",
      "dependencies": {
        "@expo/config-plugins": "~58.0.13"
      }
    },
    "node_modules/@expo/json-file": {
      "version": "11.2.1",
      "resolved": "https://registry.npmjs.org/@expo/json-file/-/json-file-11.2.1.tgz",
      "integrity": "sha512-UPhKoFCj8BcwgLB1rKQ1CuR/REITnZLiqxHEHOeH1tPsdXcHGtUDh0P5bLbr7oU0nKVdtJ5rzyKx8jniMQdESQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.20.0",
        "json5": "^2.2.3"
      }
    },
    "node_modules/@expo/local-build-cache-provider": {
      "version": "58.0.12",
      "resolved": "https://registry.npmjs.org/@expo/local-build-cache-provider/-/local-build-cache-provider-58.0.12.tgz",
      "integrity": "sha512-2fpz4A+cf7YybeVx6lc/kulUpMLOv0OrlhdcvOpMCQG/9Wp5IBOZUgykSN86wmU5ZGJe4JeDJ4Soq5H3hfvzIw==",
      "license": "MIT",
      "dependencies": {
        "@expo/config": "~58.0.12",
        "chalk": "^4.1.2"
      }
    },
    "node_modules/@expo/log-box-utils": {
      "version": "58.0.2",
      "resolved": "https://registry.npmjs.org/@expo/log-box-utils/-/log-box-utils-58.0.2.tgz",
      "integrity": "sha512-My8Lwe9FU/yDwwzqwi5LN2rzzDcJqIAZKrD9f0XHZEKz/FQnWJYdt1rsV7+RwqMGeGq2XsxTCVT1ggTCOvumxw==",
      "license": "MIT"
    },
    "node_modules/@expo/metro": {
      "version": "58.0.0",
      "resolved": "https://registry.npmjs.org/@expo/metro/-/metro-58.0.0.tgz",
      "integrity": "sha512-PMD640ihB0C3Oqm0AnDVJ/8qF2cKbRUEqGuSOr4tM/OTb9ktxsQqsiSSSeaOEgdCZBq20AxRS0d6WHNhhH2P+g==",
      "license": "MIT",
      "dependencies": {
        "metro": "0.87.1",
        "metro-babel-transformer": "0.87.1",
        "metro-cache": "0.87.1",
        "metro-cache-key": "0.87.1",
        "metro-config": "0.87.1",
        "metro-core": "0.87.1",
        "metro-file-map": "0.87.1",
        "metro-minify-terser": "0.87.1",
        "metro-resolver": "0.87.1",
        "metro-runtime": "0.87.1",
        "metro-source-map": "0.87.1",
        "metro-symbolicate": "0.87.1",
        "metro-transform-plugins": "0.87.1",
        "metro-transform-worker": "0.87.1"
      }
    },
    "node_modules/@expo/metro-file-map": {
      "version": "58.0.6",
      "resolved": "https://registry.npmjs.org/@expo/metro-file-map/-/metro-file-map-58.0.6.tgz",
      "integrity": "sha512-+kPFI328BSUxpK7OO0kM31NQlYG/z7WOTISbPEuY4fMZxmN/nLnmJIDNG8NTtM5ZHXlNPqgjRvdukxtsBEkvuw==",
      "license": "MIT",
      "dependencies": {
        "2g": "^1.0.1",
        "debug": "^4.3.4",
        "fb-watchman": "^2.0.2",
        "invariant": "^2.2.4",
        "jest-worker": "^29.7.0",
        "walker": "^1.0.8"
      }
    },
    "node_modules/@expo/modules-macros-linux-arm64": {
      "version": "0.33.0",
      "resolved": "https://registry.npmjs.org/@expo/modules-macros-linux-arm64/-/modules-macros-linux-arm64-0.33.0.tgz",
      "integrity": "sha512-5F4L/IJThOBq3oRo9NB5BI4+Od8K2YDTbU+2IHgsnXsrTc5icQtOlLwHOEfExghjo0PHCXGap4zprfOKvtANxw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@expo/modules-macros-linux-x64": {
      "version": "0.33.0",
      "resolved": "https://registry.npmjs.org/@expo/modules-macros-linux-x64/-/modules-macros-linux-x64-0.33.0.tgz",
      "integrity": "sha512-G3kxfmMpH7BDtoeBVeJA4vh5O3kQ3wmjmSfDremRBWENHKwHJXTOsyerLQqkJC39oPKCuXgXhzvp+/5qy+DyvA==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@expo/modules-macros-win32-arm64": {
      "version": "0.33.0",
      "resolved": "https://registry.npmjs.org/@expo/modules-macros-win32-arm64/-/modules-macros-win32-arm64-0.33.0.tgz",
      "integrity": "sha512-sAYEhKqywo+38UcWt1KLNzJkSkpba4HYybSSZfpFsoA28/MCBupFZggkbU/E9z81fZeuiWVA2Ote1fp8ogqRAA==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ]
    },
    "node_modules/@expo/modules-macros-win32-x64": {
      "version": "0.33.0",
      "resolved": "https://registry.npmjs.org/@expo/modules-macros-win32-x64/-/modules-macros-win32-x64-0.33.0.tgz",
      "integrity": "sha512-O7tmET8ehVpmocxpVUlXkV9yfKCNo3uKvpN7wNyWcJlEIM6xo+WZuN4RDtndExI6CE5wn8Io608US+BYtrE9+w==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ]
    },
    "node_modules/@expo/osascript": {
      "version": "2.8.1",
      "resolved": "https://registry.npmjs.org/@expo/osascript/-/osascript-2.8.1.tgz",
      "integrity": "sha512-SCi+6q6uOkGhiAn6AIP/OPFgaIq/iKD2oYpnAOg2rShHStJ8ey7wyT127RbOaZXmlcY/62rHOX1WiiMnD8u/BA==",
      "license": "MIT",
      "dependencies": {
        "@expo/spawn-async": "^1.8.0"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/@expo/package-manager": {
      "version": "1.14.2",
      "resolved": "https://registry.npmjs.org/@expo/package-manager/-/package-manager-1.14.2.tgz",
      "integrity": "sha512-sftl0eRVVCarI6grMdjAB3jX2pX1Mt3cdSnajlXS4QyeDkaKRM/ntBy6dcagj1VL0+cEfEqctlyvinmlZdNubg==",
      "license": "MIT",
      "dependencies": {
        "@expo/json-file": "^11.2.1",
        "@expo/spawn-async": "^1.8.0",
        "chalk": "^4.0.0",
        "npm-package-arg": "^11.0.0",
        "ora": "^3.4.0",
        "resolve-workspace-root": "^2.0.0"
      }
    },
    "node_modules/@expo/platforms": {
      "version": "58.0.1",
      "resolved": "https://registry.npmjs.org/@expo/platforms/-/platforms-58.0.1.tgz",
      "integrity": "sha512-KtLrtAvpShq16l9lTxd2fZSjULxcGxXrJTHA31iUVqrc+Af7aTAJW4ZB3yQBgi/w+kSb6BB/CG9RXI0ohbMm6g==",
      "license": "MIT"
    },
    "node_modules/@expo/plist": {
      "version": "0.10.2",
      "resolved": "https://registry.npmjs.org/@expo/plist/-/plist-0.10.2.tgz",
      "integrity": "sha512-kaCDdGLtezkt5s1w7iCaISNJ+RkNac/1yBYYE8XyXLSJu3czGHZKzJGQ8fFOrpEGm6GdlIHFpzVeiF01ZVyHyg==",
      "license": "MIT",
      "dependencies": {
        "@xmldom/xmldom": "^0.8.8",
        "xmlbuilder": "^15.1.1"
      }
    },
    "node_modules/@expo/prebuild-config": {
      "version": "58.0.20",
      "resolved": "https://registry.npmjs.org/@expo/prebuild-config/-/prebuild-config-58.0.20.tgz",
      "integrity": "sha512-lqXK5d6ni2MCNO/MbuXhojKC+Iy/gaYm0a3vVebwf/njoe1Fp3iw8mXDwoofmvlzZ3HO+beL7XCX6e6ZEYmVyg==",
      "license": "MIT",
      "dependencies": {
        "@expo/config": "~58.0.12",
        "@expo/config-plugins": "~58.0.13",
        "@expo/config-types": "^58.0.3",
        "@expo/image-utils": "^0.12.7",
        "@expo/json-file": "^11.2.1",
        "@react-native/normalize-colors": "0.88.1",
        "debug": "^4.3.1",
        "expo-modules-autolinking": "~58.1.0",
        "resolve-from": "^5.0.0",
        "semver": "^7.7.4"
      }
    },
    "node_modules/@expo/require-utils": {
      "version": "58.0.6",
      "resolved": "https://registry.npmjs.org/@expo/require-utils/-/require-utils-58.0.6.tgz",
      "integrity": "sha512-k9Ce7indjY3+nRBNT6wKw7NghN7pP6WhFnYNjuDiAypwjtVgaZHpD9fo0/g3/emDUpM6ebl8Ekz/teyUGfD9og==",
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.20.0",
        "@babel/core": "^7.25.2",
        "@babel/plugin-transform-modules-commonjs": "^7.24.8"
      },
      "peerDependencies": {
        "typescript": "^5.0.0 || ^5.0.0-0 || ^6.0.0 || ^7.0.0"
      },
      "peerDependenciesMeta": {
        "typescript": {
          "optional": true
        }
      }
    },
    "node_modules/@expo/schema-utils": {
      "version": "58.0.3",
      "resolved": "https://registry.npmjs.org/@expo/schema-utils/-/schema-utils-58.0.3.tgz",
      "integrity": "sha512-DwoMEpT3H+r1lU+YUEP10UcUW7sDKmfvgE7oA+zQeuGyi0XxDSDgRZUUZ5nOGp+lymmTicoIUKkoN7rByuI04g==",
      "license": "MIT"
    },
    "node_modules/@expo/sdk-runtime-versions": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/@expo/sdk-runtime-versions/-/sdk-runtime-versions-1.0.1.tgz",
      "integrity": "sha512-kvisefkhxu8Fm/4M8G6DEqUaigrXfrSOm2lFw7hsk/nq0zchcp6B4wSk8rlheHY8FRi5iHxKtoVMGY/3M6h04A==",
      "license": "MIT"
    },
    "node_modules/@expo/spawn-async": {
      "version": "1.8.0",
      "resolved": "https://registry.npmjs.org/@expo/spawn-async/-/spawn-async-1.8.0.tgz",
      "integrity": "sha512-eb9xxd/LbuEGSdua4NumCu/McVB9EM+F/JxB9pWgnERw4HQ9XyTNH1KapG6oqLWR8TuRK2LQfzJlmNi94CVobw==",
      "license": "MIT",
      "dependencies": {
        "cross-spawn": "^7.0.6"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/@expo/sudo-prompt": {
      "version": "9.3.2",
      "resolved": "https://registry.npmjs.org/@expo/sudo-prompt/-/sudo-prompt-9.3.2.tgz",
      "integrity": "sha512-HHQigo3rQWKMDzYDLkubN5WQOYXJJE2eNqIQC2axC2iO3mHdwnIR7FgZVvHWtBwAdzBgAP0ECp8KqS8TiMKvgw==",
      "license": "MIT"
    },
    "node_modules/@expo/xcpretty": {
      "version": "4.4.7",
      "resolved": "https://registry.npmjs.org/@expo/xcpretty/-/xcpretty-4.4.7.tgz",
      "integrity": "sha512-EbxYllZ7/ozONVZd425cm4XnolfW+AmSFT5aP7Jdno6oc3WrYQcHz2CO20z/2rwWwYgztmV2PXvYH+BQ8YFjqg==",
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.20.0",
        "chalk": "^4.1.0",
        "js-yaml": "^4.1.0"
      },
      "bin": {
        "excpretty": "build/cli.js"
      }
    },
    "node_modules/@isaacs/ttlcache": {
      "version": "1.4.1",
      "resolved": "https://registry.npmjs.org/@isaacs/ttlcache/-/ttlcache-1.4.1.tgz",
      "integrity": "sha512-RQgQ4uQ+pLbqXfOmieB91ejmLwvSgv9nLx6sT6sD83s7umBypgg+OIBOBbEUiJXrfpnp9j0mRhYYdzp9uqq3lA==",
      "license": "ISC",
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/@jest/schemas": {
      "version": "29.6.3",
      "resolved": "https://registry.npmjs.org/@jest/schemas/-/schemas-29.6.3.tgz",
      "integrity": "sha512-mo5j5X+jIZmJQveBKeS/clAueipV7KgiX1vMgCxam1RNYiqE1w62n0/tJJnHtjW8ZHcQco5gY85jA3mi0L+nSA==",
      "license": "MIT",
      "dependencies": {
        "@sinclair/typebox": "^0.27.8"
      },
      "engines": {
        "node": "^14.15.0 || ^16.10.0 || >=18.0.0"
      }
    },
    "node_modules/@jest/types": {
      "version": "29.6.3",
      "resolved": "https://registry.npmjs.org/@jest/types/-/types-29.6.3.tgz",
      "integrity": "sha512-u3UPsIilWKOM3F9CXtrG8LEJmNxwoCQC/XVj4IKYXvvpx7QIi/Kg1LI5uDmDpKlac62NUtX7eLjRh+jVZcLOzw==",
      "license": "MIT",
      "dependencies": {
        "@jest/schemas": "^29.6.3",
        "@types/istanbul-lib-coverage": "^2.0.0",
        "@types/istanbul-reports": "^3.0.0",
        "@types/node": "*",
        "@types/yargs": "^17.0.8",
        "chalk": "^4.0.0"
      },
      "engines": {
        "node": "^14.15.0 || ^16.10.0 || >=18.0.0"
      }
    },
    "node_modules/@jridgewell/gen-mapping": {
      "version": "0.3.13",
      "resolved": "https://registry.npmjs.org/@jridgewell/gen-mapping/-/gen-mapping-0.3.13.tgz",
      "integrity": "sha512-2kkt/7niJ6MgEPxF0bYdQ6etZaA+fQvDcLKckhy1yIQOzaoKjBBjSj63/aLVjYE3qhRt5dvM+uUyfCg6UKCBbA==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/sourcemap-codec": "^1.5.0",
        "@jridgewell/trace-mapping": "^0.3.24"
      }
    },
    "node_modules/@jridgewell/remapping": {
      "version": "2.3.5",
      "resolved": "https://registry.npmjs.org/@jridgewell/remapping/-/remapping-2.3.5.tgz",
      "integrity": "sha512-LI9u/+laYG4Ds1TDKSJW2YPrIlcVYOwi2fUC6xB43lueCjgxV4lffOCZCtYFiH6TNOX+tQKXx97T4IKHbhyHEQ==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/gen-mapping": "^0.3.5",
        "@jridgewell/trace-mapping": "^0.3.24"
      }
    },
    "node_modules/@jridgewell/resolve-uri": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/@jridgewell/resolve-uri/-/resolve-uri-3.1.3.tgz",
      "integrity": "sha512-lhTtjtoEArWBjismtfS761S9Hlyn+nIZqOZVYoZ1Xn82PMNMVnk+jj/NhC4fAXGTs7ydONcJiR5vyQBTMDu27g==",
      "license": "MIT",
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@jridgewell/source-map": {
      "version": "0.3.11",
      "resolved": "https://registry.npmjs.org/@jridgewell/source-map/-/source-map-0.3.11.tgz",
      "integrity": "sha512-ZMp1V8ZFcPG5dIWnQLr3NSI1MiCU7UETdS/A0G8V/XWHvJv3ZsFqutJn1Y5RPmAPX6F3BiE397OqveU/9NCuIA==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/gen-mapping": "^0.3.5",
        "@jridgewell/trace-mapping": "^0.3.25"
      }
    },
    "node_modules/@jridgewell/sourcemap-codec": {
      "version": "1.6.0",
      "resolved": "https://registry.npmjs.org/@jridgewell/sourcemap-codec/-/sourcemap-codec-1.6.0.tgz",
      "integrity": "sha512-T7jf+5zgsZHwNJ4lvQ7/aezbyk0nNX+zJVWpmHA7VYsEx7a7qr5Rg5IbtJFqkgze5Y2sruq1RUY8Q837Od7iFw==",
      "license": "MIT"
    },
    "node_modules/@jridgewell/trace-mapping": {
      "version": "0.3.31",
      "resolved": "https://registry.npmjs.org/@jridgewell/trace-mapping/-/trace-mapping-0.3.31.tgz",
      "integrity": "sha512-zzNR+SdQSDJzc8joaeP8QQoCQr8NuYx2dIIytl1QeBEZHJ9uW6hebsrYgbz8hJwUQao3TWCMtmfV8Nu1twOLAw==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/resolve-uri": "^3.1.0",
        "@jridgewell/sourcemap-codec": "^1.4.14"
      }
    },
    "node_modules/@noxcturnal/noxcturnal-darwin-arm64": {
      "version": "0.1.14",
      "resolved": "https://registry.npmjs.org/@noxcturnal/noxcturnal-darwin-arm64/-/noxcturnal-darwin-arm64-0.1.14.tgz",
      "integrity": "sha512-5g1fvtfmDsaDzNoqZicO7UKUUaGm9HOTJy30KNxXbSJRreLOQwK0fd0wuAA0OEbBgJSQAvVdAovpjT5HvYRIWw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@noxcturnal/noxcturnal-darwin-x64": {
      "version": "0.1.14",
      "resolved": "https://registry.npmjs.org/@noxcturnal/noxcturnal-darwin-x64/-/noxcturnal-darwin-x64-0.1.14.tgz",
      "integrity": "sha512-rnZ8LRa+rYOyHmPS2PpPgxRHaeU0zJZ7Ii8huuAMbADfJHGceGBU8SQYqd7+Vs1VwSUcxRm4BMC4+QL1IgdqrA==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@noxcturnal/noxcturnal-linux-arm64-gnu": {
      "version": "0.1.14",
      "resolved": "https://registry.npmjs.org/@noxcturnal/noxcturnal-linux-arm64-gnu/-/noxcturnal-linux-arm64-gnu-0.1.14.tgz",
      "integrity": "sha512-9SZoiNaEKwFJ0V7cgpoCjHLh80fd8/wAJrbG1VWR8DJfkbVBvXhipTnxEISZ0LdidmthpVo0i2GiI6ToUdkmkg==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@noxcturnal/noxcturnal-linux-arm64-musl": {
      "version": "0.1.14",
      "resolved": "https://registry.npmjs.org/@noxcturnal/noxcturnal-linux-arm64-musl/-/noxcturnal-linux-arm64-musl-0.1.14.tgz",
      "integrity": "sha512-dxZXo7Xj00w8eeFac+ev/75lJd/62GSUIX4wwCN2yYn6r9Jrim3DJ6yKVZwmfqHDE0v55TZsif0/vdhNFxFXfQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@noxcturnal/noxcturnal-linux-x64-gnu": {
      "version": "0.1.14",
      "resolved": "https://registry.npmjs.org/@noxcturnal/noxcturnal-linux-x64-gnu/-/noxcturnal-linux-x64-gnu-0.1.14.tgz",
      "integrity": "sha512-ek3098/TS+Ma2vJUjzpIZnhU70lryFzFPEdKdQ5u+1w00QKvMg0teFa2mec1H8/ndK74/xYWy8e4d92Uz+s9Dg==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@noxcturnal/noxcturnal-linux-x64-musl": {
      "version": "0.1.14",
      "resolved": "https://registry.npmjs.org/@noxcturnal/noxcturnal-linux-x64-musl/-/noxcturnal-linux-x64-musl-0.1.14.tgz",
      "integrity": "sha512-qblXyvGhD5HoJSK32Q8YN6PnEz4GPXgr2KLgStpRG1oG8+BRPlrqZCaQRbQI5Bn3L8NZ+OjyGWhLEG1kgdzHBw==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@noxcturnal/noxcturnal-win32-arm64-msvc": {
      "version": "0.1.14",
      "resolved": "https://registry.npmjs.org/@noxcturnal/noxcturnal-win32-arm64-msvc/-/noxcturnal-win32-arm64-msvc-0.1.14.tgz",
      "integrity": "sha512-K9Q82l32juE/p7Ca6p36rAWfNzORkCyoL0R2aDUq3tkYOmivu3xTewnxUwDLTzDIuLsMgb4niy5vrtr4IXdNXw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@noxcturnal/noxcturnal-win32-x64-msvc": {
      "version": "0.1.14",
      "resolved": "https://registry.npmjs.org/@noxcturnal/noxcturnal-win32-x64-msvc/-/noxcturnal-win32-x64-msvc-0.1.14.tgz",
      "integrity": "sha512-qiiOLLQUYnLZai3traWx90yzMLGZlkvwGNYMFkGw5MwnMifVgfl3Z3ooFiSYaVKjkTYqxBF9rOCvhFL6yXaoxA==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@oxc-project/types": {
      "version": "0.154.0",
      "resolved": "https://registry.npmjs.org/@oxc-project/types/-/types-0.154.0.tgz",
      "integrity": "sha512-KYOUGQFlLWR+s4QMV2Q9ko38TZm7EdO87Qm7rvZLqk/webse/cDjtyxKhg/47l0byCbs/k46LT8qc4PKjAikzA==",
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/oxc-project"
      }
    },
    "node_modules/@react-native/asset-utils": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/asset-utils/-/asset-utils-0.88.1.tgz",
      "integrity": "sha512-BLb5FF7NgggGYiCsA7KKkK2qFhn0K+6iGXOI+4Ucd+G7Robzw9Gt4WsWwxLt+Od+G+/hyqfz8ASokyWFZ6VcLw==",
      "license": "MIT",
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/@react-native/babel-plugin-codegen": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/babel-plugin-codegen/-/babel-plugin-codegen-0.88.1.tgz",
      "integrity": "sha512-2r7aeE3dXu3hawHNYHgazWQl9MJNjcnA/gxLApFK2gPMxBCLiQOHVUSaemDQz4mKPs5svulbhtDehxo6LzTzpQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/traverse": "^7.29.0",
        "@react-native/codegen": "0.88.1"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/@react-native/codegen": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/codegen/-/codegen-0.88.1.tgz",
      "integrity": "sha512-URPgPhnsxqeQSLyTRVzhZZ8iNXtZdR1Jop6lqaQacymvl3byghXisNIRR1YyG6PbXUfzPan5Jmz/kPhUUsZ2Yw==",
      "license": "MIT",
      "dependencies": {
        "@babel/core": "^7.25.2",
        "@babel/parser": "^7.29.0",
        "flow-parser": "0.327.0",
        "invariant": "^2.2.4",
        "nullthrows": "^1.1.1",
        "tinyglobby": "^0.2.15",
        "yargs": "^17.6.2"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      },
      "peerDependencies": {
        "@babel/core": "*"
      }
    },
    "node_modules/@react-native/codegen/node_modules/flow-estree": {
      "version": "0.327.0",
      "resolved": "https://registry.npmjs.org/flow-estree/-/flow-estree-0.327.0.tgz",
      "integrity": "sha512-f9vK751YUzD0qaHSpKc5/qQM6gqOlgGS+4ZRqTNcZOpVqn3mC55yEQ6dUG2K1eaVm5FbKkz9CFWe6XNvrkQFQg==",
      "license": "MIT",
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@react-native/codegen/node_modules/flow-parser": {
      "version": "0.327.0",
      "resolved": "https://registry.npmjs.org/flow-parser/-/flow-parser-0.327.0.tgz",
      "integrity": "sha512-/MYZ5hXWf5ozpbdfUDmazMgQXviLxWEiRLH3MppEGDdW0itRVqmB5UaU7QX+SBCDNiq+gEesSVn8nlxmPDyDkw==",
      "license": "MIT",
      "dependencies": {
        "flow-estree": "0.327.0"
      },
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/@react-native/community-cli-plugin": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/community-cli-plugin/-/community-cli-plugin-0.88.1.tgz",
      "integrity": "sha512-L2CQvzsOMz4oof6AVLSzesFL1Q92nrtXpK0uQH2VwdOmzzgkiHql8WFQSo9VLvMFGJDg8+G6enrHH573ruqqWA==",
      "license": "MIT",
      "dependencies": {
        "@react-native/asset-utils": "0.88.1",
        "@react-native/dev-middleware": "0.88.1",
        "commander": "^12.0.0",
        "debug": "^4.4.0",
        "invariant": "^2.2.4",
        "metro": "^0.87.1",
        "semver": "^7.1.3"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      },
      "peerDependencies": {
        "@react-native-community/cli": "*",
        "@react-native/metro-config": "0.88.1"
      },
      "peerDependenciesMeta": {
        "@react-native-community/cli": {
          "optional": true
        },
        "@react-native/metro-config": {
          "optional": true
        }
      }
    },
    "node_modules/@react-native/community-cli-plugin/node_modules/commander": {
      "version": "12.1.0",
      "resolved": "https://registry.npmjs.org/commander/-/commander-12.1.0.tgz",
      "integrity": "sha512-Vw8qHK3bZM9y/P10u3Vib8o/DdkvA2OtPtZvD871QKjy74Wj1WSKFILMPRPSdUSx5RFK1arlJzEtA4PkFgnbuA==",
      "license": "MIT",
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@react-native/debugger-frontend": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/debugger-frontend/-/debugger-frontend-0.88.1.tgz",
      "integrity": "sha512-4ZjH2093hZWWgsYs5ExqjzJX5uCS4R5yZa17eRHsQClUc6RjlV61kLdIk722sQReLL+NYtBn2RJtdcQtLCwiug==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/@react-native/debugger-shell": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/debugger-shell/-/debugger-shell-0.88.1.tgz",
      "integrity": "sha512-vrOLlxkp/417qcSUiS3x3gmdoQHYA/26oEKIWPB4EekJG0uJxKXsMR0tHIDiJWO0JH/2BO3M+507DjR1U74jQg==",
      "license": "MIT",
      "dependencies": {
        "cross-spawn": "^7.0.6",
        "debug": "^4.4.0",
        "fb-dotslash": "0.5.8"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/@react-native/dev-middleware": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/dev-middleware/-/dev-middleware-0.88.1.tgz",
      "integrity": "sha512-0smOWE3NCdEYUwPiEdiwVXjTdvXcwSejviCM0YZB0Dj6HaQ+uu4hpSrvgERDevr5dvtSaqr8N4TdYZCLXiVgFw==",
      "license": "MIT",
      "dependencies": {
        "@isaacs/ttlcache": "^1.4.1",
        "@react-native/debugger-frontend": "0.88.1",
        "@react-native/debugger-shell": "0.88.1",
        "connect": "^3.6.5",
        "debug": "^4.4.0",
        "invariant": "^2.2.4",
        "nullthrows": "^1.1.1",
        "open": "^8.4.2",
        "serve-static": "^1.16.2",
        "ws": "^7.5.10"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/@react-native/gradle-plugin": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/gradle-plugin/-/gradle-plugin-0.88.1.tgz",
      "integrity": "sha512-zalxoJJ/m5kxLnBy9I1zYrx4jaPxPXdys8DeROvrSOa3pSQkTwVVXRZ4FkXCdGodVA9KR2WitplDo/URNjyvFA==",
      "license": "MIT",
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/@react-native/js-polyfills": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/js-polyfills/-/js-polyfills-0.88.1.tgz",
      "integrity": "sha512-B62O6zVMYW7kK8dxIuCwpdJ5RYcIvET6ItScm0sfsTibJs+llS0krUVSAOHnEUn3lbFMfw+o+sNdWREOAc6FfQ==",
      "license": "MIT",
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/@react-native/normalize-colors": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/normalize-colors/-/normalize-colors-0.88.1.tgz",
      "integrity": "sha512-2SAKiLyZRf+peBLkhhJWGY5vC26w1Uj9QBgUZvjAnOxjgeEKUGBE5riPS0R7+YoqSrRL0w8ucwZB4M+vvy9HMg==",
      "license": "MIT"
    },
    "node_modules/@react-native/virtualized-lists": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/@react-native/virtualized-lists/-/virtualized-lists-0.88.1.tgz",
      "integrity": "sha512-Zt+OGvJE6VgmzgemZL8TSA0VomNWpHMNcG0OvLkkBQEGrzY8OdDHRfjJh7S+f+UFJF77kicRC6o6mt3A7ER9lQ==",
      "license": "MIT",
      "dependencies": {
        "invariant": "^2.2.4",
        "nullthrows": "^1.1.1"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      },
      "peerDependencies": {
        "@types/react": "^19.2.0",
        "react": "*",
        "react-native": "0.88.1"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@sinclair/typebox": {
      "version": "0.27.12",
      "resolved": "https://registry.npmjs.org/@sinclair/typebox/-/typebox-0.27.12.tgz",
      "integrity": "sha512-hhyNJ+nbR6ZR7pToHvllEFun9TL0sbL+tk/ON75lo+Xas054uez98qRbsuNt7MBCyZKK4+8Yli/OAGZhmfBZ/g==",
      "license": "MIT"
    },
    "node_modules/@types/istanbul-lib-coverage": {
      "version": "2.0.6",
      "resolved": "https://registry.npmjs.org/@types/istanbul-lib-coverage/-/istanbul-lib-coverage-2.0.6.tgz",
      "integrity": "sha512-2QF/t/auWm0lsy8XtKVPG19v3sSOQlJe/YHZgfjb/KBBHOGSV+J2q/S671rcq9uTBrLAXmZpqJiaQbMT+zNU1w==",
      "license": "MIT"
    },
    "node_modules/@types/istanbul-lib-report": {
      "version": "3.0.3",
      "resolved": "https://registry.npmjs.org/@types/istanbul-lib-report/-/istanbul-lib-report-3.0.3.tgz",
      "integrity": "sha512-NQn7AHQnk/RSLOxrBbGyJM/aVQ+pjj5HCgasFxc0K/KhoATfQ/47AyUl15I2yBUpihjmas+a+VJBOqecrFH+uA==",
      "license": "MIT",
      "dependencies": {
        "@types/istanbul-lib-coverage": "*"
      }
    },
    "node_modules/@types/istanbul-reports": {
      "version": "3.0.4",
      "resolved": "https://registry.npmjs.org/@types/istanbul-reports/-/istanbul-reports-3.0.4.tgz",
      "integrity": "sha512-pk2B1NWalF9toCRu6gjBzR69syFjP4Od8WRAX+0mmf9lAjCRicLOWc+ZrxZHx/0XRjotgkF9t6iaMJ+aXcOdZQ==",
      "license": "MIT",
      "dependencies": {
        "@types/istanbul-lib-report": "*"
      }
    },
    "node_modules/@types/node": {
      "version": "26.6.6",
      "resolved": "https://registry.npmjs.org/@types/node/-/node-26.6.6.tgz",
      "integrity": "sha512-MzQj+8Kx3XI40OmUAE6Qoh58ZMNstNNMwn2nfd3qWsfe7nDNSqJNzes4njhz6AHwrSHOffSLwXU6yb474Q4aog==",
      "license": "MIT",
      "dependencies": {
        "undici-types": "~8.9.0"
      }
    },
    "node_modules/@types/react": {
      "version": "19.3.0",
      "resolved": "https://registry.npmjs.org/@types/react/-/react-19.3.0.tgz",
      "integrity": "sha512-N0rFCuH9YoxG9/m61l9MfpJKfmLOVU0em7ipIz6TRgSSkvReLB9vL85GB+yr8Bs5leqpvg96JSwF4ZS1s4viQg==",
      "devOptional": true,
      "license": "MIT",
      "dependencies": {
        "csstype": "^3.2.2"
      }
    },
    "node_modules/@types/yargs": {
      "version": "17.0.35",
      "resolved": "https://registry.npmjs.org/@types/yargs/-/yargs-17.0.35.tgz",
      "integrity": "sha512-qUHkeCyQFxMXg79wQfTtfndEC+N9ZZg76HJftDJp+qH2tV7Gj4OJi7l+PiWwJ+pWtW8GwSmqsDj/oymhrTWXjg==",
      "license": "MIT",
      "dependencies": {
        "@types/yargs-parser": "*"
      }
    },
    "node_modules/@types/yargs-parser": {
      "version": "21.0.3",
      "resolved": "https://registry.npmjs.org/@types/yargs-parser/-/yargs-parser-21.0.3.tgz",
      "integrity": "sha512-I4q9QU9MQv4oEOz4tAHJtNz1cwuLxn2F3xcc2iV5WdqLPpUnj30aUuxt1mAxYTG+oe8CZMV/+6rU4S4gRDzqtQ==",
      "license": "MIT"
    },
    "node_modules/@ungap/structured-clone": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/@ungap/structured-clone/-/structured-clone-1.4.0.tgz",
      "integrity": "sha512-1mEZtMKPM09vDmQt5y7YvmN2+DFTP7Tg0EWXdic8/C6VRnpb33e4ghisCIE3WZjsE2N8mf+QV1Zqh7ZFYLWInQ==",
      "license": "ISC"
    },
    "node_modules/@xmldom/xmldom": {
      "version": "0.8.15",
      "resolved": "https://registry.npmjs.org/@xmldom/xmldom/-/xmldom-0.8.15.tgz",
      "integrity": "sha512-/5NV/vDALVFDXgLmfsy9TRCBlKwO2LNBFzpzvb9iIj+jR+eSc6DLYYvVOdivT/jm7MtU6TebYuRmzEOI7w40UA==",
      "license": "MIT",
      "engines": {
        "node": ">=10.0.0"
      }
    },
    "node_modules/2g": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/2g/-/2g-1.0.1.tgz",
      "integrity": "sha512-+uViadKOS/wwR4pFu5g8TPn3QHpKqoX19JHCnp8k/3cLpImdcXozwvZA6Q/5PeW3AcU8neL8faaMidBcv7o8CA==",
      "license": "MIT",
      "bin": {
        "2g": "bin/cli.js"
      },
      "peerDependencies": {
        "typescript": ">=5.8.0"
      },
      "peerDependenciesMeta": {
        "typescript": {
          "optional": true
        }
      }
    },
    "node_modules/accepts": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/accepts/-/accepts-2.0.0.tgz",
      "integrity": "sha512-5cvg6CtKwfgdmVqY1WIiXKc3Q1bkRqGLi+2W/6ao+6Y7gu/RCwRuAhGEzh5B4KlszSuTLgZYuqFqo5bImjNKng==",
      "license": "MIT",
      "dependencies": {
        "mime-types": "^3.0.0",
        "negotiator": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/acorn": {
      "version": "8.19.0",
      "resolved": "https://registry.npmjs.org/acorn/-/acorn-8.19.0.tgz",
      "integrity": "sha512-oJlA3XiRm7Cyk6qFD2Jn8ak9B7jSy0qy00ADO3+8dpT0LSjFihQYv4C02LFCSYJV3Q37xYwwRy5m+IpIiUzqWw==",
      "license": "MIT",
      "bin": {
        "acorn": "bin/acorn"
      },
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/agent-base": {
      "version": "7.1.4",
      "resolved": "https://registry.npmjs.org/agent-base/-/agent-base-7.1.4.tgz",
      "integrity": "sha512-MnA+YT8fwfJPgBx3m60MNqakm30XOkyIoH1y6huTQvC0PwZG7ki8NacLBcrPbNoo8vEZy7Jpuk7+jMO+CUovTQ==",
      "license": "MIT",
      "engines": {
        "node": ">= 14"
      }
    },
    "node_modules/agent-cli-detector": {
      "version": "0.1.7",
      "resolved": "https://registry.npmjs.org/agent-cli-detector/-/agent-cli-detector-0.1.7.tgz",
      "integrity": "sha512-d8OWDVdZMgjhLUT9ZPgSv/BdFFF9pVuscC0JdUSz3bjwE15gcp6u/o0/JooM2yyAWC49KThFhXlgTXRa9B7yng==",
      "license": "MIT",
      "bin": {
        "agent-cli-detector": "dist/cli.js"
      },
      "engines": {
        "node": ">=18.18"
      }
    },
    "node_modules/anser": {
      "version": "1.4.10",
      "resolved": "https://registry.npmjs.org/anser/-/anser-1.4.10.tgz",
      "integrity": "sha512-hCv9AqTQ8ycjpSd3upOJd7vFwW1JaoYQ7tpham03GJ1ca8/65rqn0RpaWpItOAd6ylW9wAw6luXYPJIyPFVOww==",
      "license": "MIT"
    },
    "node_modules/ansi-escapes": {
      "version": "4.3.2",
      "resolved": "https://registry.npmjs.org/ansi-escapes/-/ansi-escapes-4.3.2.tgz",
      "integrity": "sha512-gKXj5ALrKWQLsYG9jlTRmR/xKluxHV+Z9QEwNIgCfM1/uwPMCuzVVnh5mwTd+OuBZcwSIMbqssNWRm1lE51QaQ==",
      "license": "MIT",
      "dependencies": {
        "type-fest": "^0.21.3"
      },
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/ansi-escapes/node_modules/type-fest": {
      "version": "0.21.3",
      "resolved": "https://registry.npmjs.org/type-fest/-/type-fest-0.21.3.tgz",
      "integrity": "sha512-t0rzBq87m3fVcduHDUFhKmyyX+9eo6WQjZvf51Ea/M0Q7+T374Jp1aUiyUl0GKxp8M/OETVHSDvmkyPgvX+X2w==",
      "license": "(MIT OR CC0-1.0)",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/ansi-regex": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-5.0.1.tgz",
      "integrity": "sha512-quJQXlTSUGL2LH9SUXo8VwsY4soanhgo6LNSm84E1LBcE8s3O0wpdiRzyR9z/ZZJMlMWv37qOOb9pdJlMUEKFQ==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/ansi-styles": {
      "version": "4.3.0",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-4.3.0.tgz",
      "integrity": "sha512-zbB9rCJAT1rbjiVDb2hqKFHNYLxgtk8NURxZ3IZwD3F6NtxbXZQCnnSi1Lkx+IDohdPlFp222wVALIheZJQSEg==",
      "license": "MIT",
      "dependencies": {
        "color-convert": "^2.0.1"
      },
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-styles?sponsor=1"
      }
    },
    "node_modules/arg": {
      "version": "5.0.2",
      "resolved": "https://registry.npmjs.org/arg/-/arg-5.0.2.tgz",
      "integrity": "sha512-PYjyFOLKQ9y57JvQ6QLo8dAgNqswh8M1RMJYdQduT6xbWSgK36P/Z/v+p888pM69jMMfS8Xd8F6I1kQ/I9HUGg==",
      "license": "MIT"
    },
    "node_modules/argparse": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/argparse/-/argparse-2.0.1.tgz",
      "integrity": "sha512-8+9WqebbFzpX9OR+Wa6O29asIogeRMzcGtAINdpMHHyAg10f05aSFVBbcEqGf/PXw1EjAZ+q2/bEBg3DvurK3Q==",
      "license": "Python-2.0"
    },
    "node_modules/asap": {
      "version": "2.0.6",
      "resolved": "https://registry.npmjs.org/asap/-/asap-2.0.6.tgz",
      "integrity": "sha512-BSHWgDSAiKs50o2Re8ppvp3seVHXSRM44cdSsT9FfNEUUZLOGWVCsiWaRPWM1Znn+mqZ1OfVZ3z3DWEzSp7hRA==",
      "license": "MIT"
    },
    "node_modules/babel-plugin-polyfill-corejs2": {
      "version": "0.4.17",
      "resolved": "https://registry.npmjs.org/babel-plugin-polyfill-corejs2/-/babel-plugin-polyfill-corejs2-0.4.17.tgz",
      "integrity": "sha512-aTyf30K/rqAsNwN76zYrdtx8obu0E4KoUME29B1xj+B3WxgvWkp943vYQ+z8Mv3lw9xHXMHpvSPOBxzAkIa94w==",
      "license": "MIT",
      "dependencies": {
        "@babel/compat-data": "^7.28.6",
        "@babel/helper-define-polyfill-provider": "^0.6.8",
        "semver": "^6.3.1"
      },
      "peerDependencies": {
        "@babel/core": "^7.4.0 || ^8.0.0-0 <8.0.0"
      }
    },
    "node_modules/babel-plugin-polyfill-corejs2/node_modules/semver": {
      "version": "6.3.2",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.2.tgz",
      "integrity": "sha512-GYrCADwpu6yV5OAvchkQ27Z5wwMxWAEMg5NNWjyHh/5DboFFqbdbvYNIvZouQpxXyeMPoTOh0vdPYKlf0ZswdQ==",
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/babel-plugin-polyfill-corejs3": {
      "version": "0.13.0",
      "resolved": "https://registry.npmjs.org/babel-plugin-polyfill-corejs3/-/babel-plugin-polyfill-corejs3-0.13.0.tgz",
      "integrity": "sha512-U+GNwMdSFgzVmfhNm8GJUX88AadB3uo9KpJqS3FaqNIPKgySuvMb+bHPsOmmuWyIcuqZj/pzt1RUIUZns4y2+A==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-define-polyfill-provider": "^0.6.5",
        "core-js-compat": "^3.43.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.4.0 || ^8.0.0-0 <8.0.0"
      }
    },
    "node_modules/babel-plugin-polyfill-regenerator": {
      "version": "0.6.8",
      "resolved": "https://registry.npmjs.org/babel-plugin-polyfill-regenerator/-/babel-plugin-polyfill-regenerator-0.6.8.tgz",
      "integrity": "sha512-M762rNHfSF1EV3SLtnCJXFoQbbIIz0OyRwnCmV0KPC7qosSfCO0QLTSuJX3ayAebubhE6oYBAYPrBA5ljowaZg==",
      "license": "MIT",
      "dependencies": {
        "@babel/helper-define-polyfill-provider": "^0.6.8"
      },
      "peerDependencies": {
        "@babel/core": "^7.4.0 || ^8.0.0-0 <8.0.0"
      }
    },
    "node_modules/babel-plugin-react-compiler": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/babel-plugin-react-compiler/-/babel-plugin-react-compiler-1.0.0.tgz",
      "integrity": "sha512-Ixm8tFfoKKIPYdCCKYTsqv+Fd4IJ0DQqMyEimo+pxUOMUR9cVPlwTrFt9Avu+3cb6Zp3mAzl+t1MrG2fxxKsxw==",
      "license": "MIT",
      "dependencies": {
        "@babel/types": "^7.26.0"
      }
    },
    "node_modules/babel-plugin-react-native-web": {
      "version": "0.21.4",
      "resolved": "https://registry.npmjs.org/babel-plugin-react-native-web/-/babel-plugin-react-native-web-0.21.4.tgz",
      "integrity": "sha512-FSclsDTGi5EcvpbW3TM7s8GLWwQqo5wI9zQqJr2m0IoJRenSkp1+bVvdeZXTNznI5Ms9Bry7DLBR+C5Shb9gtw==",
      "license": "MIT"
    },
    "node_modules/babel-plugin-syntax-hermes-parser": {
      "version": "0.36.1",
      "resolved": "https://registry.npmjs.org/babel-plugin-syntax-hermes-parser/-/babel-plugin-syntax-hermes-parser-0.36.1.tgz",
      "integrity": "sha512-ycduwJbvdvIMmVvlAZqGggS+pm5Eu4Bk9pcV9Sm2Z4PJNRVsKkv0g7vHj+LeuC1gHTeF67sJXFOq61IlqCa2hA==",
      "license": "MIT",
      "dependencies": {
        "hermes-parser": "0.36.1"
      }
    },
    "node_modules/babel-plugin-transform-flow-enums": {
      "version": "0.0.2",
      "resolved": "https://registry.npmjs.org/babel-plugin-transform-flow-enums/-/babel-plugin-transform-flow-enums-0.0.2.tgz",
      "integrity": "sha512-g4aaCrDDOsWjbm0PUUeVnkcVd6AKJsVc/MbnPhEotEpkeJQP6b8nzewohQi7+QS8UyPehOhGWn0nOwjvWpmMvQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/plugin-syntax-flow": "^7.12.1"
      }
    },
    "node_modules/balanced-match": {
      "version": "4.0.4",
      "resolved": "https://registry.npmjs.org/balanced-match/-/balanced-match-4.0.4.tgz",
      "integrity": "sha512-BLrgEcRTwX2o6gGxGOCNyMvGSp35YofuYzw9h1IMTRmKqttAZZVU67bdb9Pr2vUHA8+j3i2tJfjO6C6+4myGTA==",
      "license": "MIT",
      "engines": {
        "node": "18 || 20 || >=22"
      }
    },
    "node_modules/base64-js": {
      "version": "1.5.1",
      "resolved": "https://registry.npmjs.org/base64-js/-/base64-js-1.5.1.tgz",
      "integrity": "sha512-AKpaYlHn8t4SVbOHCy+b5+KKgvR4vrsD8vbvrbiQJps7fKDTkjkDry6ji0rUJjC0kzbNePLwzxq8iypo41qeWA==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/feross"
        },
        {
          "type": "patreon",
          "url": "https://www.patreon.com/feross"
        },
        {
          "type": "consulting",
          "url": "https://feross.org/support"
        }
      ],
      "license": "MIT"
    },
    "node_modules/baseline-browser-mapping": {
      "version": "2.11.39",
      "resolved": "https://registry.npmjs.org/baseline-browser-mapping/-/baseline-browser-mapping-2.11.39.tgz",
      "integrity": "sha512-Q9buOYhr2ggrEZpImICecZTJHCCd8yXkRUokFlUEQ8uiD6oP82F4W4jWnhOHZYV+wlvrC51V7Wy0ULyWjil5Wg==",
      "license": "Apache-2.0",
      "bin": {
        "baseline-browser-mapping": "dist/cli.cjs"
      },
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/big-integer": {
      "version": "1.6.52",
      "resolved": "https://registry.npmjs.org/big-integer/-/big-integer-1.6.52.tgz",
      "integrity": "sha512-QxD8cf2eVqJOOz63z6JIN9BzvVs/dlySa5HGSBH5xtR8dPteIRQnBxxKqkNTiT6jbDTF6jAfrd4oMcND9RGbQg==",
      "license": "Unlicense",
      "engines": {
        "node": ">=0.6"
      }
    },
    "node_modules/bplist-creator": {
      "version": "0.1.0",
      "resolved": "https://registry.npmjs.org/bplist-creator/-/bplist-creator-0.1.0.tgz",
      "integrity": "sha512-sXaHZicyEEmY86WyueLTQesbeoH/mquvarJaQNbjuOQO+7gbFcDEWqKmcWA4cOTLzFlfgvkiVxolk1k5bBIpmg==",
      "license": "MIT",
      "dependencies": {
        "stream-buffers": "2.2.x"
      }
    },
    "node_modules/bplist-parser": {
      "version": "0.3.1",
      "resolved": "https://registry.npmjs.org/bplist-parser/-/bplist-parser-0.3.1.tgz",
      "integrity": "sha512-PyJxiNtA5T2PlLIeBot4lbp7rj4OadzjnMZD/G5zuBNt8ei/yCU7+wW0h2bag9vr8c+/WuRWmSxbqAl9hL1rBA==",
      "license": "MIT",
      "dependencies": {
        "big-integer": "1.6.x"
      },
      "engines": {
        "node": ">= 5.10.0"
      }
    },
    "node_modules/brace-expansion": {
      "version": "5.1.0",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-5.1.0.tgz",
      "integrity": "sha512-aa11Dv491GKnYqxaul3aRJ0szew7yMJMfZPnqD44NjGrZXoj62l41OEDDpdpC4eE2P88vBFfLuSyRhpG91NUvg==",
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^4.0.2"
      },
      "engines": {
        "node": "20 || >=22"
      }
    },
    "node_modules/braces": {
      "version": "3.0.3",
      "resolved": "https://registry.npmjs.org/braces/-/braces-3.0.3.tgz",
      "integrity": "sha512-yQbXgO/OSZVD2IsiLlro+7Hf6Q18EJrKSEsdoMzKePKXct3gvD8oLcOQdIzGupr5Fj+EDe8gO/lxc1BzfMpxvA==",
      "license": "MIT",
      "dependencies": {
        "fill-range": "^7.1.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/browserslist": {
      "version": "4.29.6",
      "resolved": "https://registry.npmjs.org/browserslist/-/browserslist-4.29.6.tgz",
      "integrity": "sha512-CmVVIQ3RVc5HxYEc9X84GvxK/C8C1wH8TlKAiO7uTxF8PDwt7r8t9Qk3J9NkMOVzX5O/HbLv3yzxZg9HPrnI9w==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "baseline-browser-mapping": "^2.11.37",
        "caniuse-lite": "^1.0.30001826",
        "electron-to-chromium": "^1.5.486",
        "node-releases": "^2.0.64",
        "update-browserslist-db": "^1.4.0"
      },
      "bin": {
        "browserslist": "cli.js"
      },
      "engines": {
        "node": "^6 || ^7 || ^8 || ^9 || ^10 || ^11 || ^12 || >=13.7"
      }
    },
    "node_modules/bser": {
      "version": "2.1.2",
      "resolved": "https://registry.npmjs.org/bser/-/bser-2.1.2.tgz",
      "integrity": "sha512-V2o8YS2EhrKMO9AumnkK0ynynfFlsajpYupwq7S46H5mhcanwxDkNTw3K67wPIcKTH1ffkA4vhMOtAc7gRmPZw==",
      "license": "MIT",
      "dependencies": {
        "node-int64": "^0.4.0"
      }
    },
    "node_modules/buffer-from": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/buffer-from/-/buffer-from-1.1.2.tgz",
      "integrity": "sha512-E+XQCRwSbaaiChtv6k6Dwgc+bx+Bs6vuKJHHl5kox/BaKbhiXzqQOwK4cO22yElGp2OCmjwVhT3HmxgyPGnJfQ==",
      "license": "MIT"
    },
    "node_modules/bytes": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/bytes/-/bytes-3.1.2.tgz",
      "integrity": "sha512-/Nf7TyzTx6S3yRJObOAV7956r8cr2+Oj8AC5dt8wSP3BQAoeX58NoHyCU8P8zGkNXStjTSi6fzO6F0pBdcYbEg==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/camelcase": {
      "version": "6.3.0",
      "resolved": "https://registry.npmjs.org/camelcase/-/camelcase-6.3.0.tgz",
      "integrity": "sha512-Gmy6FhYlCY7uOElZUSbxo2UCDH8owEk996gkbrpsgGtrJLM3J7jGxl9Ic7Qwwj4ivOE5AWZWRMecDdF7hqGjFA==",
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/caniuse-lite": {
      "version": "1.0.30001827",
      "resolved": "https://registry.npmjs.org/caniuse-lite/-/caniuse-lite-1.0.30001827.tgz",
      "integrity": "sha512-YWEDr46gSO81M8w6uPbaIy4++IXsirx2asUqvllNiD4BPf75ibxclUjWEqp8ObCenRv+UM2n5Y8xuRPT8V8FrQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/caniuse-lite"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "CC-BY-4.0"
    },
    "node_modules/chalk": {
      "version": "4.1.2",
      "resolved": "https://registry.npmjs.org/chalk/-/chalk-4.1.2.tgz",
      "integrity": "sha512-oKnbhFyRIXpUuez8iBMmyEa4nbj4IOQyuhc/wy9kY7/WVPcwIO9VA668Pu8RkO7+0G76SLROeyw9CpQ061i4mA==",
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^4.1.0",
        "supports-color": "^7.1.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/chalk?sponsor=1"
      }
    },
    "node_modules/ci-info": {
      "version": "3.9.0",
      "resolved": "https://registry.npmjs.org/ci-info/-/ci-info-3.9.0.tgz",
      "integrity": "sha512-NIxF55hv4nSqQswkAeiOi1r83xy8JldOFDTWiug55KBu9Jnblncd2U6ViHmYgHf01TPZS77NJBhBMKdWj9HQMQ==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/sibiraj-s"
        }
      ],
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/cli-cursor": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/cli-cursor/-/cli-cursor-2.1.0.tgz",
      "integrity": "sha512-8lgKz8LmCRYZZQDpRyT2m5rKJ08TnU4tR9FFFW2rxpxR1FzWi4PQ/NfyODchAatHaUgnSPVcx/R5w6NuTBzFiw==",
      "license": "MIT",
      "dependencies": {
        "restore-cursor": "^2.0.0"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/cli-spinners": {
      "version": "2.9.2",
      "resolved": "https://registry.npmjs.org/cli-spinners/-/cli-spinners-2.9.2.tgz",
      "integrity": "sha512-ywqV+5MmyL4E7ybXgKys4DugZbX0FC6LnwrhjuykIjnK9k8OQacQ7axGKnjDXWNhns0xot3bZI5h55H8yo9cJg==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/cliui": {
      "version": "8.0.1",
      "resolved": "https://registry.npmjs.org/cliui/-/cliui-8.0.1.tgz",
      "integrity": "sha512-BSeNnyus75C4//NQ9gQt1/csTXyo/8Sb+afLAkzAptFuMsod9HFokGNudZpi/oQV73hnVK+sR+5PVRMd+Dr7YQ==",
      "license": "ISC",
      "dependencies": {
        "string-width": "^4.2.0",
        "strip-ansi": "^6.0.1",
        "wrap-ansi": "^7.0.0"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/clone": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/clone/-/clone-1.0.4.tgz",
      "integrity": "sha512-JQHZ2QMW6l3aH/j6xCqQThY/9OH4D/9ls34cgkUBiEeocRTU04tHfKPBsUK1PqZCUQM7GiA0IIXJSuXHI64Kbg==",
      "license": "MIT",
      "engines": {
        "node": ">=0.8"
      }
    },
    "node_modules/color-convert": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-2.0.1.tgz",
      "integrity": "sha512-RRECPsj7iu/xb5oKYcsFHSppFNnsj/52OVTRKb4zP5onXwVF3zVmmToNcOfGC+CRDpfK/U584fMg38ZHCaElKQ==",
      "license": "MIT",
      "dependencies": {
        "color-name": "~1.1.4"
      },
      "engines": {
        "node": ">=7.0.0"
      }
    },
    "node_modules/color-name": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.4.tgz",
      "integrity": "sha512-dOy+3AuW3a2wNbZHIuMZpTcgjGuLU/uBL/ubcZF9OXbDo8ff4O8yVp5Bf0efS8uEoYo5q4Fx7dY9OgQGXgAsQA==",
      "license": "MIT"
    },
    "node_modules/commander": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/commander/-/commander-7.2.0.tgz",
      "integrity": "sha512-QrWXB+ZQSVPmIWIhtEO9H+gwHaMGYiF5ChvoJ+K9ZGHG/sVsa6yiesAD1GC/x46sET00Xlwo1u49RVVVzvcSkw==",
      "license": "MIT",
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/compressible": {
      "version": "2.0.18",
      "resolved": "https://registry.npmjs.org/compressible/-/compressible-2.0.18.tgz",
      "integrity": "sha512-AF3r7P5dWxL8MxyITRMlORQNaOA2IkAFaTr4k7BUumjPtRpGDTZpl0Pb1XCO6JeDCBdp126Cgs9sMxqSjgYyRg==",
      "license": "MIT",
      "dependencies": {
        "mime-db": ">= 1.43.0 < 2"
      },
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/compression": {
      "version": "1.8.2",
      "resolved": "https://registry.npmjs.org/compression/-/compression-1.8.2.tgz",
      "integrity": "sha512-o8vI5RE5A6EVVOd9o41jKp41aJom+QTEO/Bx8MYNjexMo/Bv2WOjUfZr+aL0WnYSgymUy6zeguqLTsIhV0gMvQ==",
      "license": "MIT",
      "dependencies": {
        "bytes": "3.1.2",
        "compressible": "~2.0.18",
        "debug": "2.6.9",
        "destroy": "1.2.0",
        "negotiator": "~0.6.4",
        "on-headers": "~1.1.0",
        "safe-buffer": "5.2.1",
        "vary": "~1.1.2"
      },
      "engines": {
        "node": ">= 0.8.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/express"
      }
    },
    "node_modules/compression/node_modules/debug": {
      "version": "2.6.9",
      "resolved": "https://registry.npmjs.org/debug/-/debug-2.6.9.tgz",
      "integrity": "sha512-bC7ElrdJaJnPbAP+1EotYvqZsb3ecl5wi6Bfi6BJTUcNowp6cvspg0jXznRTKDjm/E7AdgFBVeAPVMNcKGsHMA==",
      "license": "MIT",
      "dependencies": {
        "ms": "2.0.0"
      }
    },
    "node_modules/compression/node_modules/ms": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/ms/-/ms-2.0.0.tgz",
      "integrity": "sha512-Tpp60P6IUJDTuOq/5Z8cdskzJujfwqfOTkrwIwj7IRISpnkJnT6SyJ4PCPnGMoFjC9ddhal5KVIYtAt97ix05A==",
      "license": "MIT"
    },
    "node_modules/compression/node_modules/negotiator": {
      "version": "0.6.4",
      "resolved": "https://registry.npmjs.org/negotiator/-/negotiator-0.6.4.tgz",
      "integrity": "sha512-myRT3DiWPHqho5PrJaIRyaMv2kgYf0mUVgBNOYMuCH5Ki1yEiQaf/ZJuQ62nvpc44wL5WDbTX7yGJi1Neevw8w==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/connect": {
      "version": "3.7.0",
      "resolved": "https://registry.npmjs.org/connect/-/connect-3.7.0.tgz",
      "integrity": "sha512-ZqRXc+tZukToSNmh5C2iWMSoV3X1YUcPbqEM4DkEG5tNQXrQUZCNVGGv3IuicnkMtPfGf3Xtp8WCXs295iQ1pQ==",
      "license": "MIT",
      "dependencies": {
        "debug": "2.6.9",
        "finalhandler": "1.1.2",
        "parseurl": "~1.3.3",
        "utils-merge": "1.0.1"
      },
      "engines": {
        "node": ">= 0.10.0"
      }
    },
    "node_modules/connect/node_modules/debug": {
      "version": "2.6.9",
      "resolved": "https://registry.npmjs.org/debug/-/debug-2.6.9.tgz",
      "integrity": "sha512-bC7ElrdJaJnPbAP+1EotYvqZsb3ecl5wi6Bfi6BJTUcNowp6cvspg0jXznRTKDjm/E7AdgFBVeAPVMNcKGsHMA==",
      "license": "MIT",
      "dependencies": {
        "ms": "2.0.0"
      }
    },
    "node_modules/connect/node_modules/ms": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/ms/-/ms-2.0.0.tgz",
      "integrity": "sha512-Tpp60P6IUJDTuOq/5Z8cdskzJujfwqfOTkrwIwj7IRISpnkJnT6SyJ4PCPnGMoFjC9ddhal5KVIYtAt97ix05A==",
      "license": "MIT"
    },
    "node_modules/content-type": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/content-type/-/content-type-2.1.0.tgz",
      "integrity": "sha512-mj7UPXE0jaqaOsukNZRUEfEi2AcL7C/vwmwcHV0O97eO1E1pxBZuyjlZrx5seTaNBg1U6+o35wpa35Qfcc+7ag==",
      "license": "MIT",
      "engines": {
        "node": ">=18"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/express"
      }
    },
    "node_modules/convert-source-map": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/convert-source-map/-/convert-source-map-2.0.0.tgz",
      "integrity": "sha512-Kvp459HrV2FEJ1CAsi1Ku+MY3kasH19TFykTz2xWmMeq6bk2NU3XXvfJ+Q61m0xktWwt+1HSYf3JZsTms3aRJg==",
      "license": "MIT"
    },
    "node_modules/core-js-compat": {
      "version": "3.51.0",
      "resolved": "https://registry.npmjs.org/core-js-compat/-/core-js-compat-3.51.0.tgz",
      "integrity": "sha512-52r6fkXgxv4GLMjmFcMWRx7X9bw071xTTdrDcdyPGRqU2oE+9pCG0bAOMifSBdLw0JRBZKEF0q3B55qPlLuE8g==",
      "license": "MIT",
      "dependencies": {
        "browserslist": "^4.29.3"
      },
      "engines": {
        "node": ">=6.4.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/core-js"
      }
    },
    "node_modules/cross-spawn": {
      "version": "7.0.6",
      "resolved": "https://registry.npmjs.org/cross-spawn/-/cross-spawn-7.0.6.tgz",
      "integrity": "sha512-uV2QOWP2nWzsy2aMp8aRibhi9dlzF5Hgh5SHaB9OiTGEyDTiJJyx0uy51QXdyWbtAHNua4XJzUKca3OzKUd3vA==",
      "license": "MIT",
      "dependencies": {
        "path-key": "^3.1.0",
        "shebang-command": "^2.0.0",
        "which": "^2.0.1"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/csstype": {
      "version": "3.2.4",
      "resolved": "https://registry.npmjs.org/csstype/-/csstype-3.2.4.tgz",
      "integrity": "sha512-PoKaoPzQapnEoqUSnHx1u6W6ku8CVEgKsnpmmzU3m1nwkidpPBQ8V/Zq2+bWNrsOKoKLwTGdbx6xF7BXP1zLVQ==",
      "devOptional": true,
      "license": "MIT"
    },
    "node_modules/debug": {
      "version": "4.4.3",
      "resolved": "https://registry.npmjs.org/debug/-/debug-4.4.3.tgz",
      "integrity": "sha512-RGwwWnwQvkVfavKVt22FGLw+xYSdzARwm0ru6DhTVA3umU5hZc28V3kO4stgYryrTlLpuvgI9GiijltAjNbcqA==",
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.3"
      },
      "engines": {
        "node": ">=6.0"
      },
      "peerDependenciesMeta": {
        "supports-color": {
          "optional": true
        }
      }
    },
    "node_modules/defaults": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/defaults/-/defaults-1.0.4.tgz",
      "integrity": "sha512-eFuaLoy/Rxalv2kr+lqMlUnrDWV+3j4pljOIJgLIhI058IQfWJ7vXhyEIHu+HtC738klGALYxOKDO0bQP3tg8A==",
      "license": "MIT",
      "dependencies": {
        "clone": "^1.0.2"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/define-lazy-prop": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/define-lazy-prop/-/define-lazy-prop-2.0.0.tgz",
      "integrity": "sha512-Ds09qNh8yw3khSjiJjiUInaGX9xlqZDY7JVryGxdxV7NPeuqQfplOpQ66yJFZut3jLa5zOwkXw1g9EI2uKh4Og==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/depd": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/depd/-/depd-2.0.0.tgz",
      "integrity": "sha512-g7nH6P6dyDioJogAAGprGpCtVImJhpPk/roCzdb3fIh61/s/nPsfR6onyMwkCAR/OlC3yBC0lESvUoQEAssIrw==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/destroy": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/destroy/-/destroy-1.2.0.tgz",
      "integrity": "sha512-2sJGJTaXIIaR1w4iJSNoN0hnMY7Gpc/n8D4qSCJw8QqFWXf7cuAgnEHxBpweaVcPevC2l3KpjYCx3NypQQgaJg==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8",
        "npm": "1.2.8000 || >= 1.4.16"
      }
    },
    "node_modules/detect-libc": {
      "version": "2.1.2",
      "resolved": "https://registry.npmjs.org/detect-libc/-/detect-libc-2.1.2.tgz",
      "integrity": "sha512-Btj2BOOO83o3WyH59e8MgXsxEQVcarkUOpEYrubB0urwnN10yQ364rsiByU11nZlqWYZm05i/of7io4mzihBtQ==",
      "license": "Apache-2.0",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/dnssd-advertise": {
      "version": "1.1.6",
      "resolved": "https://registry.npmjs.org/dnssd-advertise/-/dnssd-advertise-1.1.6.tgz",
      "integrity": "sha512-Ndrrf6BMPalkQPd/zubL+4YghH2J9NspapQ09uDXwYbvOPkP0oaqf5CkcwJ0b50kS2O3ul6yVu+jz+RY62Cejg==",
      "license": "MIT"
    },
    "node_modules/ee-first": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/ee-first/-/ee-first-1.1.1.tgz",
      "integrity": "sha512-WMwm9LhRUo+WUaRN+vRuETqG89IgZphVSNkdFgeb6sS/E4OrDIN7t48CAewSHXc6C8lefD8KKfr5vY61brQlow==",
      "license": "MIT"
    },
    "node_modules/electron-to-chromium": {
      "version": "1.5.493",
      "resolved": "https://registry.npmjs.org/electron-to-chromium/-/electron-to-chromium-1.5.493.tgz",
      "integrity": "sha512-/Wto2sKd0EpepzMqwSP2il2TNc+rnBDF6k1poCvhRKpaSSD4sLGRBE+FydqHs2QwcW9cXKLVDqnauzJy1oByYw==",
      "license": "ISC"
    },
    "node_modules/emoji-regex": {
      "version": "8.0.0",
      "resolved": "https://registry.npmjs.org/emoji-regex/-/emoji-regex-8.0.0.tgz",
      "integrity": "sha512-MSjYzcWNOA0ewAHpz0MxpYFvwg6yjy1NG3xteoqz644VCo/RPgnr1/GGt+ic3iJTzQ8Eu3TdM14SawnVUmGE6A==",
      "license": "MIT"
    },
    "node_modules/encodeurl": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/encodeurl/-/encodeurl-1.0.4.tgz",
      "integrity": "sha512-ImAQpWtQZKdkUxvj9CMNzB8M4IGg0DkRTZzmOHqgVFrf71JDmUacbt+iKljfIpD2yHcxI+HR76d8bwvdvtSvGA==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/error-stack-parser": {
      "version": "2.1.4",
      "resolved": "https://registry.npmjs.org/error-stack-parser/-/error-stack-parser-2.1.4.tgz",
      "integrity": "sha512-Sk5V6wVazPhq5MhpO+AUxJn5x7XSXGl1R93Vn7i+zS15KDVxQijejNCrz8340/2bgLBjR9GtEG8ZVKONDjcqGQ==",
      "license": "MIT",
      "dependencies": {
        "stackframe": "^1.3.4"
      }
    },
    "node_modules/es-errors": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/es-errors/-/es-errors-1.3.0.tgz",
      "integrity": "sha512-Zf5H2Kxt2xjTvbJvP2ZWLEICxA6j+hAmMzIlypy4xcBg1vKVnx89Wy0GbS+kf5cwCVFFzdCFh2XSCFNULS6csw==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/escalade": {
      "version": "3.2.0",
      "resolved": "https://registry.npmjs.org/escalade/-/escalade-3.2.0.tgz",
      "integrity": "sha512-WUj2qlxaQtO4g6Pq5c29GTcWGDyd8itL8zTlipgECz3JesAiiOKotd8JU6otB3PACgG6xkJUyVhboMS+bje/jA==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/escape-html": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/escape-html/-/escape-html-1.0.3.tgz",
      "integrity": "sha512-NiSupZ4OeuGwr68lGIeym/ksIZMJodUGOSCZ/FSnTxcrekbvqrgdUxlJOMpijaKZVjAJrWrGs/6Jy8OMuyj9ow==",
      "license": "MIT"
    },
    "node_modules/escape-string-regexp": {
      "version": "1.0.5",
      "resolved": "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-1.0.5.tgz",
      "integrity": "sha512-vbRorB5FUQWvla16U8R/qgaFIya2qGzwDrNmCZuYKrbdSUMG6I1ZCGQRefkRVhuOkIGVne7BQ35DSfo1qvJqFg==",
      "license": "MIT",
      "engines": {
        "node": ">=0.8.0"
      }
    },
    "node_modules/etag": {
      "version": "1.8.1",
      "resolved": "https://registry.npmjs.org/etag/-/etag-1.8.1.tgz",
      "integrity": "sha512-aIL5Fx7mawVa300al2BnEE4iNvo1qETxLrPI/o05L7z6go7fCw1J6EQmbK4FmJ2AS7kgVF/KEZWufBfdClMcPg==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/expo": {
      "version": "58.0.26",
      "resolved": "https://registry.npmjs.org/expo/-/expo-58.0.26.tgz",
      "integrity": "sha512-6i4kqt5lbcQdxmtnkkJ3JR5sn+A3L+xO45duLhh2rndvrek/chX/GTysTYozl4oL3+txKD53pDlJd75XRYf9Ow==",
      "license": "MIT",
      "dependencies": {
        "@babel/runtime": "^7.20.0",
        "@expo/cli": "^58.1.21",
        "@expo/config": "~58.0.12",
        "@expo/config-plugins": "~58.0.13",
        "@expo/devtools": "~58.0.2",
        "@expo/dom-webview": "~58.0.2",
        "@expo/fingerprint": "^0.21.10",
        "@expo/local-build-cache-provider": "^58.0.12",
        "@expo/log-box": "^58.0.15",
        "@expo/log-box-utils": "^58.0.2",
        "@expo/metro": "~58.0.0",
        "@expo/metro-config": "~58.0.23",
        "@ungap/structured-clone": "^1.3.0",
        "babel-preset-expo": "~58.0.26",
        "expo-asset": "~58.0.21",
        "expo-constants": "~58.0.16",
        "expo-file-system": "~58.0.14",
        "expo-font": "~58.0.12",
        "expo-keep-awake": "~58.0.4",
        "expo-modules-autolinking": "~58.1.0",
        "expo-modules-cli": "~0.5.0",
        "expo-modules-core": "~58.1.0",
        "pretty-format": "^29.7.0",
        "react-refresh": "^0.14.2",
        "whatwg-url-minimum": "^0.2.0"
      },
      "bin": {
        "expo": "bin/cli",
        "expo-modules": "bin/modules",
        "expo-modules-autolinking": "bin/autolinking",
        "fingerprint": "bin/fingerprint"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || ^26.0.0 || >=27.0.0"
      },
      "peerDependencies": {
        "@expo/dom-webview": "*",
        "@expo/metro-runtime": "*",
        "react": "*",
        "react-dom": "*",
        "react-native": "*",
        "react-native-web": "*",
        "react-native-webview": "*"
      },
      "peerDependenciesMeta": {
        "@expo/dom-webview": {
          "optional": true
        },
        "@expo/metro-runtime": {
          "optional": true
        },
        "react-dom": {
          "optional": true
        },
        "react-native-web": {
          "optional": true
        },
        "react-native-webview": {
          "optional": true
        }
      }
    },
    "node_modules/expo-modules-autolinking": {
      "version": "58.1.0",
      "resolved": "https://registry.npmjs.org/expo-modules-autolinking/-/expo-modules-autolinking-58.1.0.tgz",
      "integrity": "sha512-JAegkS+nC4LVEgKMHAnpWhUxs1BYHHaTJnncVW2EQION1bVz0y8/wEglAeGV+oq4BNS1V7s8zCMTZU0hMi28bA==",
      "license": "MIT",
      "dependencies": {
        "@expo/platforms": "^58.0.1",
        "@expo/require-utils": "^58.0.6",
        "@expo/spawn-async": "^1.8.0",
        "chalk": "^4.1.0",
        "commander": "^7.2.0"
      },
      "bin": {
        "expo-modules-autolinking": "bin/expo-modules-autolinking.js"
      }
    },
    "node_modules/expo-modules-cli": {
      "version": "0.5.0",
      "resolved": "https://registry.npmjs.org/expo-modules-cli/-/expo-modules-cli-0.5.0.tgz",
      "integrity": "sha512-uBNKkp5NIMo2bmJiQL36EBLNMeX+2GEIxpz10BioT0EGQTsPcgrV0ypfGy31GtPoFOObyc9ibHhklsOtpzhblw==",
      "license": "MIT",
      "dependencies": {
        "@babel/parser": "^7.20.0",
        "arg": "^5.0.2"
      },
      "bin": {
        "expo-modules": "bin/expo-modules.js"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || ^26.0.0 || >=27.0.0"
      }
    },
    "node_modules/expo-modules-core": {
      "version": "58.1.0",
      "resolved": "https://registry.npmjs.org/expo-modules-core/-/expo-modules-core-58.1.0.tgz",
      "integrity": "sha512-eXHOPyxHkDyTxUWnKEatC+Hx4tLoPWCPd5pCynAU4WkaBvAG/l5t/wu5jXiE5eh2CRr2NU4iAQePX2zUfNEVhA==",
      "license": "MIT",
      "dependencies": {
        "expo-modules-jsi": "~58.0.23",
        "expo-modules-macros": "0.33.0",
        "invariant": "^2.2.4"
      },
      "peerDependencies": {
        "react": "*",
        "react-native": "*",
        "react-native-worklets": ">=0.13.0"
      },
      "peerDependenciesMeta": {
        "react-native-worklets": {
          "optional": true
        }
      }
    },
    "node_modules/expo-modules-jsi": {
      "version": "58.0.23",
      "resolved": "https://registry.npmjs.org/expo-modules-jsi/-/expo-modules-jsi-58.0.23.tgz",
      "integrity": "sha512-ex3CnT8KLubsPjUG0RpEL5VgmpnWxf7Ouc+WXEr8jEbIwqcULEWtA2tfhGZwjg6jS3zeNwjygF1w8QSstP7JfQ==",
      "license": "MIT",
      "peerDependencies": {
        "react-native": "*"
      }
    },
    "node_modules/expo-modules-macros": {
      "version": "0.33.0",
      "resolved": "https://registry.npmjs.org/expo-modules-macros/-/expo-modules-macros-0.33.0.tgz",
      "integrity": "sha512-ddrT2jbYPYmiHmzcYOixRemFUUK9qQEb5pOBWgoFoW0gj3sGld1CZX0GwblUXeZMyEX65S9vc1bEhIAGVDRA9w==",
      "license": "MIT",
      "optionalDependencies": {
        "@expo/modules-macros-linux-arm64": "0.33.0",
        "@expo/modules-macros-linux-x64": "0.33.0",
        "@expo/modules-macros-win32-arm64": "0.33.0",
        "@expo/modules-macros-win32-x64": "0.33.0"
      }
    },
    "node_modules/expo-secure-store": {
      "version": "58.0.3",
      "resolved": "https://registry.npmjs.org/expo-secure-store/-/expo-secure-store-58.0.3.tgz",
      "integrity": "sha512-RpubZfqJREEcwKbx3HFoWbtDd31t+yESMj7Ei5/mGQp5vViwUBzL4nUCZRLFyt+O690mT8We7dDtIUZeIk6LbQ==",
      "license": "MIT",
      "peerDependencies": {
        "expo": "*"
      }
    },
    "node_modules/expo-server": {
      "version": "58.1.0",
      "resolved": "https://registry.npmjs.org/expo-server/-/expo-server-58.1.0.tgz",
      "integrity": "sha512-jo7I6uHnP5OQYKx3+7lbpdVVnOEwFj2ryDkQdauUQSwgh2HuMUkiFXWUIVe01ts6DLRoff5U0Tv+uNb3CMq/kw==",
      "license": "MIT",
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || ^26.0.0 || >=27.0.0"
      }
    },
    "node_modules/expo-status-bar": {
      "version": "58.0.5",
      "resolved": "https://registry.npmjs.org/expo-status-bar/-/expo-status-bar-58.0.5.tgz",
      "integrity": "sha512-Lq1h7QpNY2FY7+Dyrn15atrFZs1Yd4IfMfhwyyWb3TqWc+vwtYZH54W9VhhjqXtgitXe+RVAX7YZoCekjbLmug==",
      "license": "MIT",
      "peerDependencies": {
        "expo": "*",
        "react": "*",
        "react-native": "*"
      }
    },
    "node_modules/expo/node_modules/@expo/cli": {
      "version": "58.1.21",
      "resolved": "https://registry.npmjs.org/@expo/cli/-/cli-58.1.21.tgz",
      "integrity": "sha512-E+27FQ1Y26fVb0p1wVHBFkbe5oQubUXLwF/au5Vy8OCqDWrmbekBQamRI4mBhY15FhZQxAkyK0e6hXcEFKVBOw==",
      "license": "MIT",
      "dependencies": {
        "@expo/code-signing-certificates": "^0.0.7",
        "@expo/config": "~58.0.12",
        "@expo/config-plugins": "~58.0.13",
        "@expo/devcert": "^1.2.2",
        "@expo/env": "~2.6.0",
        "@expo/image-utils": "^0.12.7",
        "@expo/inline-modules": "^0.2.10",
        "@expo/json-file": "^11.2.1",
        "@expo/log-box": "^58.0.15",
        "@expo/log-box-utils": "^58.0.2",
        "@expo/metro": "~58.0.0",
        "@expo/metro-config": "58.0.23",
        "@expo/metro-file-map": "^58.0.6",
        "@expo/osascript": "^2.8.1",
        "@expo/package-manager": "^1.14.2",
        "@expo/platforms": "^58.0.1",
        "@expo/plist": "^0.10.2",
        "@expo/prebuild-config": "^58.0.20",
        "@expo/require-utils": "^58.0.6",
        "@expo/router-server": "^58.0.23",
        "@expo/schema-utils": "^58.0.3",
        "@expo/spawn-async": "^1.8.0",
        "@expo/ws-tunnel": "^2.0.1",
        "@expo/xcpretty": "^4.4.6",
        "@react-native/asset-utils": "0.88.1",
        "@react-native/dev-middleware": "0.88.1",
        "@react-native/js-polyfills": "0.88.1",
        "2g": "^1.0.1",
        "accepts": "^1.3.8",
        "agent-cli-detector": "0.1.7",
        "arg": "^5.0.2",
        "bplist-creator": "0.1.0",
        "bplist-parser": "^0.3.1",
        "chalk": "^4.0.0",
        "ci-info": "^3.3.0",
        "compression": "^1.7.4",
        "connect": "^3.7.0",
        "dnssd-advertise": "^1.1.6",
        "expo-server": "^58.1.0",
        "fetch-nodeshim": "^0.4.10",
        "lan-network": "^0.2.1",
        "multitars": "^1.0.2",
        "node-forge": "^1.4.0",
        "npm-package-arg": "^11.0.0",
        "ora": "^3.4.0",
        "picomatch": "^4.0.4",
        "pretty-format": "^29.7.0",
        "progress": "^2.0.3",
        "prompts": "^2.3.2",
        "resolve-from": "^5.0.0",
        "sandbox-cli-detector": "^0.2.0",
        "semver": "^7.7.4",
        "send": "^0.19.0",
        "slugify": "^1.3.4",
        "stacktrace-parser": "^0.1.10",
        "structured-headers": "^0.4.1",
        "terminal-link": "^2.1.1",
        "tinyglobby": "^0.2.15",
        "toqr": "^0.1.1",
        "wrap-ansi": "^7.0.0",
        "ws": "^8.12.1"
      },
      "bin": {
        "expo-internal": "bin/cli.js"
      },
      "peerDependencies": {
        "expo": "*",
        "expo-mcp": "*",
        "expo-router": "*",
        "react-native": "*"
      },
      "peerDependenciesMeta": {
        "expo-mcp": {
          "optional": true
        },
        "expo-router": {
          "optional": true
        },
        "react-native": {
          "optional": true
        }
      }
    },
    "node_modules/expo/node_modules/@expo/cli/node_modules/@expo/router-server": {
      "version": "58.0.23",
      "resolved": "https://registry.npmjs.org/@expo/router-server/-/router-server-58.0.23.tgz",
      "integrity": "sha512-Vcd/mskn2BSGt9dVAzAKlUFGbagfUlMT3afTgkw7KDpn8pwtkbm6M4g11158OcVSZ10m3VLvoySeZDFPskHLaQ==",
      "license": "MIT",
      "dependencies": {
        "debug": "^4.3.4"
      },
      "peerDependencies": {
        "@expo/metro-runtime": "^58.0.17",
        "expo": "*",
        "expo-constants": "^58.0.16",
        "expo-font": "^58.0.12",
        "expo-router": "*",
        "expo-server": "^58.1.0",
        "react": "*",
        "react-dom": "*",
        "react-server-dom-webpack": "~19.0.1 || ~19.1.2 || ~19.2.1 || ~19.3.0"
      },
      "peerDependenciesMeta": {
        "@expo/metro-runtime": {
          "optional": true
        },
        "expo-router": {
          "optional": true
        },
        "react-dom": {
          "optional": true
        },
        "react-server-dom-webpack": {
          "optional": true
        }
      }
    },
    "node_modules/expo/node_modules/@expo/devtools": {
      "version": "58.0.2",
      "resolved": "https://registry.npmjs.org/@expo/devtools/-/devtools-58.0.2.tgz",
      "integrity": "sha512-WBj/K+vv8JPSmY70ennL04YYOHkpEsGGkfuVY9lfv4XO7Qhbt5qz4q6W7maME194I5oGcimRMigUFfWNkBe90w==",
      "license": "MIT",
      "dependencies": {
        "chalk": "^4.1.2"
      },
      "peerDependencies": {
        "expo": "*",
        "react": "*",
        "react-native": "*"
      },
      "peerDependenciesMeta": {
        "expo": {
          "optional": true
        },
        "react": {
          "optional": true
        },
        "react-native": {
          "optional": true
        }
      }
    },
    "node_modules/expo/node_modules/@expo/dom-webview": {
      "version": "58.0.2",
      "resolved": "https://registry.npmjs.org/@expo/dom-webview/-/dom-webview-58.0.2.tgz",
      "integrity": "sha512-bLkREoP7qL3rEuzxP60xG+TjdPoGjbnZfxkvYo5imJxGWfKMOf7x962W06Pu+WWAr4gcDRk16iA+Clg8D0zjCg==",
      "license": "MIT",
      "peerDependencies": {
        "expo": "*",
        "react": "*",
        "react-native": "*"
      }
    },
    "node_modules/expo/node_modules/@expo/log-box": {
      "version": "58.0.15",
      "resolved": "https://registry.npmjs.org/@expo/log-box/-/log-box-58.0.15.tgz",
      "integrity": "sha512-IBpaJcTdJlSqmiEtyI9XDiNPSRUZNpeWdRbzE4ic6I4k17mpy0LxWJ4Mz2hB7B48b9BrleUKFeZ+6VseglmvGQ==",
      "license": "MIT",
      "dependencies": {
        "@expo/dom-webview": "^58.0.2",
        "@expo/log-box-utils": "^58.0.2",
        "anser": "^1.4.9",
        "stacktrace-parser": "^0.1.10"
      },
      "peerDependencies": {
        "@expo/dom-webview": "^58.0.2",
        "expo": "*",
        "react": "*",
        "react-native": "*"
      },
      "peerDependenciesMeta": {
        "expo": {
          "optional": true
        }
      }
    },
    "node_modules/expo/node_modules/@expo/metro-config": {
      "version": "58.0.23",
      "resolved": "https://registry.npmjs.org/@expo/metro-config/-/metro-config-58.0.23.tgz",
      "integrity": "sha512-cEFdrMxH4cddH9rHDg2FxUAl4FUC7TBs8d8GYE1r+zXOjsScoKrQhMtLOPqIc2VEj3ehUFvto3EycrEgrWck+A==",
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.20.0",
        "@babel/core": "^7.20.0",
        "@babel/generator": "^7.20.5",
        "@expo/config": "~58.0.12",
        "@expo/env": "~2.6.0",
        "@expo/json-file": "~11.2.1",
        "@expo/metro": "~58.0.0",
        "@expo/platforms": "^58.0.1",
        "@expo/require-utils": "^58.0.6",
        "@expo/spawn-async": "^1.8.0",
        "@jridgewell/gen-mapping": "^0.3.13",
        "@jridgewell/remapping": "^2.3.5",
        "@jridgewell/sourcemap-codec": "^1.5.5",
        "@jridgewell/trace-mapping": "^0.3.31",
        "@react-native/js-polyfills": "0.88.1",
        "2g": "^1.0.1",
        "browserslist": "^4.25.0",
        "chalk": "^4.1.0",
        "debug": "^4.3.2",
        "hermes-parser": "^0.36.0",
        "jsc-safe-url": "^0.2.4",
        "lightningcss": "^1.30.1",
        "noxcturnal": "^0.1.14",
        "picomatch": "^4.0.4",
        "postcss": "^8.5.23",
        "resolve-from": "^5.0.0",
        "tinyglobby": "^0.2.15"
      },
      "peerDependencies": {
        "expo": "*"
      },
      "peerDependenciesMeta": {
        "expo": {
          "optional": true
        }
      }
    },
    "node_modules/expo/node_modules/@expo/ws-tunnel": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/@expo/ws-tunnel/-/ws-tunnel-2.0.1.tgz",
      "integrity": "sha512-mljsRffbOHzmSimYQbQu9h9NR3alwCCwEEouRGFL4QRTt8dNvsNtKEPa/5jHmtDLDtsh4xXsWKwzjN9BTpeXHQ==",
      "license": "MIT",
      "peerDependencies": {
        "ws": "^8.0.0"
      }
    },
    "node_modules/expo/node_modules/accepts": {
      "version": "1.3.8",
      "resolved": "https://registry.npmjs.org/accepts/-/accepts-1.3.8.tgz",
      "integrity": "sha512-PYAthTa2m2VKxuvSD3DPC/Gy+U+sOA1LAuT8mkmRuvw+NACSaeXEQ+NHcVF7rONl6qcaxV3Uuemwawk+7+SJLw==",
      "license": "MIT",
      "dependencies": {
        "mime-types": "~2.1.34",
        "negotiator": "0.6.3"
      },
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/expo/node_modules/babel-preset-expo": {
      "version": "58.0.26",
      "resolved": "https://registry.npmjs.org/babel-preset-expo/-/babel-preset-expo-58.0.26.tgz",
      "integrity": "sha512-ZCH0nRF6T5Txn2r7FqY66xcYN2ni80WzH3snBA0pFGHZpMeSgaADnb5jJmPGEnWKcb7p34ViGFf17jXoFQ1zGg==",
      "license": "MIT",
      "dependencies": {
        "@babel/generator": "^7.20.5",
        "@babel/helper-module-imports": "^7.25.9",
        "@babel/plugin-proposal-decorators": "^7.12.9",
        "@babel/plugin-proposal-export-default-from": "^7.24.7",
        "@babel/plugin-syntax-dynamic-import": "^7.8.3",
        "@babel/plugin-syntax-export-default-from": "^7.24.7",
        "@babel/plugin-syntax-nullish-coalescing-operator": "^7.8.3",
        "@babel/plugin-syntax-optional-chaining": "^7.8.3",
        "@babel/plugin-transform-async-generator-functions": "^7.25.4",
        "@babel/plugin-transform-async-to-generator": "^7.24.7",
        "@babel/plugin-transform-block-scoping": "^7.25.0",
        "@babel/plugin-transform-class-properties": "^7.25.4",
        "@babel/plugin-transform-class-static-block": "^7.27.1",
        "@babel/plugin-transform-classes": "^7.25.4",
        "@babel/plugin-transform-destructuring": "^7.24.8",
        "@babel/plugin-transform-export-namespace-from": "^7.25.9",
        "@babel/plugin-transform-flow-strip-types": "^7.25.2",
        "@babel/plugin-transform-for-of": "^7.24.7",
        "@babel/plugin-transform-logical-assignment-operators": "^7.24.7",
        "@babel/plugin-transform-modules-commonjs": "^7.24.8",
        "@babel/plugin-transform-named-capturing-groups-regex": "^7.24.7",
        "@babel/plugin-transform-nullish-coalescing-operator": "^7.24.7",
        "@babel/plugin-transform-object-rest-spread": "^7.24.7",
        "@babel/plugin-transform-optional-catch-binding": "^7.24.7",
        "@babel/plugin-transform-optional-chaining": "^7.24.8",
        "@babel/plugin-transform-parameters": "^7.24.7",
        "@babel/plugin-transform-private-methods": "^7.24.7",
        "@babel/plugin-transform-private-property-in-object": "^7.24.7",
        "@babel/plugin-transform-react-display-name": "^7.24.7",
        "@babel/plugin-transform-react-jsx": "^7.28.6",
        "@babel/plugin-transform-react-jsx-development": "^7.27.1",
        "@babel/plugin-transform-react-pure-annotations": "^7.27.1",
        "@babel/plugin-transform-runtime": "^7.24.7",
        "@babel/plugin-transform-typescript": "^7.25.2",
        "@babel/plugin-transform-unicode-regex": "^7.24.7",
        "@babel/preset-typescript": "^7.23.0",
        "@react-native/babel-plugin-codegen": "0.88.1",
        "babel-plugin-react-compiler": "^1.0.0",
        "babel-plugin-react-native-web": "~0.21.4",
        "babel-plugin-syntax-hermes-parser": "^0.36.0",
        "babel-plugin-transform-flow-enums": "^0.0.2",
        "debug": "^4.3.4"
      },
      "peerDependencies": {
        "@babel/runtime": "^7.20.0",
        "expo": "*",
        "expo-widgets": "^58.0.29",
        "react-refresh": ">=0.14.0 <1.0.0"
      },
      "peerDependenciesMeta": {
        "@babel/runtime": {
          "optional": true
        },
        "expo": {
          "optional": true
        },
        "expo-widgets": {
          "optional": true
        }
      }
    },
    "node_modules/expo/node_modules/expo-asset": {
      "version": "58.0.21",
      "resolved": "https://registry.npmjs.org/expo-asset/-/expo-asset-58.0.21.tgz",
      "integrity": "sha512-qaJmuTtswggXdBQfiUdpxrVGM7l+tH8iEDHwVDMuxyCF/kAau8sUGVuWrDKYNW4yAx7Z8ncgsT8s27pXjRH5GA==",
      "license": "MIT",
      "dependencies": {
        "@expo/image-utils": "^0.12.7",
        "expo-constants": "~58.0.16"
      },
      "peerDependencies": {
        "expo": "*",
        "react": "*",
        "react-native": "*"
      }
    },
    "node_modules/expo/node_modules/expo-constants": {
      "version": "58.0.16",
      "resolved": "https://registry.npmjs.org/expo-constants/-/expo-constants-58.0.16.tgz",
      "integrity": "sha512-sVETnE1ktBMclc2Ve3qNrHhOCCio75a9JdghnJYGbqblmKfrrfE+lO9K4g9kNtmslIBLTK9Dyty6PbubkXs3Yw==",
      "license": "MIT",
      "dependencies": {
        "@expo/env": "~2.6.0",
        "@expo/require-utils": "^58.0.6"
      },
      "peerDependencies": {
        "expo": "*",
        "react-native": "*"
      }
    },
    "node_modules/expo/node_modules/expo-file-system": {
      "version": "58.0.14",
      "resolved": "https://registry.npmjs.org/expo-file-system/-/expo-file-system-58.0.14.tgz",
      "integrity": "sha512-VK67RQPDmWRHGbvpmPY5MeA1Ulw1LiyKs4KIN8na/q7SlkxYuPPR8biWsyX1S1/8XAHm6y2txUnYjCKh9l93lQ==",
      "license": "MIT",
      "peerDependencies": {
        "expo": "*",
        "react-native": "*"
      }
    },
    "node_modules/expo/node_modules/expo-font": {
      "version": "58.0.12",
      "resolved": "https://registry.npmjs.org/expo-font/-/expo-font-58.0.12.tgz",
      "integrity": "sha512-5m8TJrQ27DT1815P066HBtcHINgD8yuIqH4ca2ZyYwCsPa4QZ8UzOBDtrHnAMWMAlAgol+PGVj9aKeoYov70JA==",
      "license": "MIT",
      "peerDependencies": {
        "expo": "*",
        "react": "*",
        "react-native": "*"
      }
    },
    "node_modules/expo/node_modules/expo-keep-awake": {
      "version": "58.0.4",
      "resolved": "https://registry.npmjs.org/expo-keep-awake/-/expo-keep-awake-58.0.4.tgz",
      "integrity": "sha512-zXJJRBwMpWl2Q2Aj9rksMe1ncz6aphOPqYnG3rTkCFALZiM22xQCqpQqBloDcQ6g4RdGTy++lRnsDX7MWpK1qw==",
      "license": "MIT",
      "peerDependencies": {
        "expo": "*",
        "react": "*"
      }
    },
    "node_modules/expo/node_modules/mime-db": {
      "version": "1.52.0",
      "resolved": "https://registry.npmjs.org/mime-db/-/mime-db-1.52.0.tgz",
      "integrity": "sha512-sPU4uV7dYlvtWJxwwxHD0PuihVNiE7TyAbQ5SWxDCB9mUYvOgroQOwYQQOKPJ8CIbE+1ETVlOoK1UC2nU3gYvg==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/expo/node_modules/mime-types": {
      "version": "2.1.35",
      "resolved": "https://registry.npmjs.org/mime-types/-/mime-types-2.1.35.tgz",
      "integrity": "sha512-ZDY+bPm5zTTF+YpCrAU9nK0UgICYPT0QtT1NZWFv4s++TNkcgVaT0g6+4R2uI4MjQjzysHB1zxuWL50hzaeXiw==",
      "license": "MIT",
      "dependencies": {
        "mime-db": "1.52.0"
      },
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/expo/node_modules/negotiator": {
      "version": "0.6.3",
      "resolved": "https://registry.npmjs.org/negotiator/-/negotiator-0.6.3.tgz",
      "integrity": "sha512-+EUsqGPLsM+j/zdChZjsnX51g4XrHFOIXwfnCVPGlQk/k5giakcKsuxCObBRu6DSm9opw/O6slWbJdghQM4bBg==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/expo/node_modules/picomatch": {
      "version": "4.0.7",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-4.0.7.tgz",
      "integrity": "sha512-qcJu88Q2IWqJsDD529JKMdwGm/dvInW4HvQnRwiH9JtihJvzGOscDtHE3x1pBKeUOTysQ8kVmLnJ2kJu7yhcGA==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/expo/node_modules/ws": {
      "version": "8.23.0",
      "resolved": "https://registry.npmjs.org/ws/-/ws-8.23.0.tgz",
      "integrity": "sha512-wCkmX8QMOrKjgO8HW2WyDbTSGeqkocxgDzS9iR79rEAexty6/2qzilx3Ag8Tqf9ykop3irLKle0MtVn5qjVnoQ==",
      "license": "MIT",
      "engines": {
        "node": ">=10.0.0"
      },
      "peerDependencies": {
        "bufferutil": "^4.0.1",
        "utf-8-validate": ">=5.0.2"
      },
      "peerDependenciesMeta": {
        "bufferutil": {
          "optional": true
        },
        "utf-8-validate": {
          "optional": true
        }
      }
    },
    "node_modules/exponential-backoff": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/exponential-backoff/-/exponential-backoff-3.1.3.tgz",
      "integrity": "sha512-ZgEeZXj30q+I0EN+CbSSpIyPaJ5HVQD18Z1m+u1FXbAeT94mr1zw50q4q6jiiC447Nl/YTcIYSAftiGqetwXCA==",
      "license": "Apache-2.0"
    },
    "node_modules/fb-dotslash": {
      "version": "0.5.8",
      "resolved": "https://registry.npmjs.org/fb-dotslash/-/fb-dotslash-0.5.8.tgz",
      "integrity": "sha512-XHYLKk9J4BupDxi9bSEhkfss0m+Vr9ChTrjhf9l2iw3jB5C7BnY4GVPoMcqbrTutsKJso6yj2nAB6BI/F2oZaA==",
      "license": "(MIT OR Apache-2.0)",
      "bin": {
        "dotslash": "bin/dotslash"
      },
      "engines": {
        "node": ">=20"
      }
    },
    "node_modules/fb-watchman": {
      "version": "2.0.4",
      "resolved": "https://registry.npmjs.org/fb-watchman/-/fb-watchman-2.0.4.tgz",
      "integrity": "sha512-tGQtaoYisPDriJBN0mT5yZSyNETnJGA1gTYxaVRAE5KUO3LI9kPUc9WIu8JXcxaIci+faIKlzXqXyPgrmubtBQ==",
      "license": "MIT",
      "dependencies": {
        "bser": "2.1.2"
      }
    },
    "node_modules/fetch-nodeshim": {
      "version": "0.4.11",
      "resolved": "https://registry.npmjs.org/fetch-nodeshim/-/fetch-nodeshim-0.4.11.tgz",
      "integrity": "sha512-mdKkKZtNfL3PAK940FSnTgA5XhsGP2IZTE4mv6UoJxixPnslS2oG02Oz06BzH88QwDOJtXRaFqABIJ2Zha6h2A==",
      "license": "MIT"
    },
    "node_modules/fill-range": {
      "version": "7.1.1",
      "resolved": "https://registry.npmjs.org/fill-range/-/fill-range-7.1.1.tgz",
      "integrity": "sha512-YsGpe3WHLK8ZYi4tWDg2Jy3ebRz2rXowDxnld4bkQB00cc/1Zw9AWnC0i9ztDJitivtQvaI9KaLyKrc+hBW0yg==",
      "license": "MIT",
      "dependencies": {
        "to-regex-range": "^5.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/finalhandler": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/finalhandler/-/finalhandler-1.1.2.tgz",
      "integrity": "sha512-aAWcW57uxVNrQZqFXjITpW3sIUQmHGG3qSb9mUah9MgMC4NeWhNOlNjXEYq3HjRAvL6arUviZGGJsBg6z0zsWA==",
      "license": "MIT",
      "dependencies": {
        "debug": "2.6.9",
        "encodeurl": "~1.0.2",
        "escape-html": "~1.0.3",
        "on-finished": "~2.3.0",
        "parseurl": "~1.3.3",
        "statuses": "~1.5.0",
        "unpipe": "~1.0.0"
      },
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/finalhandler/node_modules/debug": {
      "version": "2.6.9",
      "resolved": "https://registry.npmjs.org/debug/-/debug-2.6.9.tgz",
      "integrity": "sha512-bC7ElrdJaJnPbAP+1EotYvqZsb3ecl5wi6Bfi6BJTUcNowp6cvspg0jXznRTKDjm/E7AdgFBVeAPVMNcKGsHMA==",
      "license": "MIT",
      "dependencies": {
        "ms": "2.0.0"
      }
    },
    "node_modules/finalhandler/node_modules/ms": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/ms/-/ms-2.0.0.tgz",
      "integrity": "sha512-Tpp60P6IUJDTuOq/5Z8cdskzJujfwqfOTkrwIwj7IRISpnkJnT6SyJ4PCPnGMoFjC9ddhal5KVIYtAt97ix05A==",
      "license": "MIT"
    },
    "node_modules/flow-enums-runtime": {
      "version": "0.0.6",
      "resolved": "https://registry.npmjs.org/flow-enums-runtime/-/flow-enums-runtime-0.0.6.tgz",
      "integrity": "sha512-3PYnM29RFXwvAN6Pc/scUfkI7RwhQ/xqyLUyPNlXUp9S40zI8nup9tUSrTLSVnWGBN38FNiGWbwZOB6uR4OGdw==",
      "license": "MIT"
    },
    "node_modules/flow-estree": {
      "version": "0.331.0",
      "resolved": "https://registry.npmjs.org/flow-estree/-/flow-estree-0.331.0.tgz",
      "integrity": "sha512-FVLYkSL/ITb/QXBEQvNWPjPooRGswuUtGOwrH+puSlMDneNkxy640+FZsk/TfKL+b7Wbw/Fg9FTUv2bMQDpj2w==",
      "license": "MIT",
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/flow-parser": {
      "version": "0.331.0",
      "resolved": "https://registry.npmjs.org/flow-parser/-/flow-parser-0.331.0.tgz",
      "integrity": "sha512-vEZcHIlnKeN8JSVtYFczj8sWJfHIJOkz+YG00O/oul/Bete+t1ZhTi+O6JRRLFYvGW+yJkZ0YgL16iStnbkUqQ==",
      "license": "MIT",
      "dependencies": {
        "flow-estree": "0.331.0"
      },
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/fresh": {
      "version": "0.5.2",
      "resolved": "https://registry.npmjs.org/fresh/-/fresh-0.5.2.tgz",
      "integrity": "sha512-zJ2mQYM18rEFOudeV4GShTGIQ7RbzA7ozbU9I/XBpm7kqgMywgmylMwXHxZJmkVoYkna9d2pVXVXPdYTP9ej8Q==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/function-bind": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/function-bind/-/function-bind-1.1.2.tgz",
      "integrity": "sha512-7XHNxH7qX9xG5mIwxkhumTox/MIRNcOgDrxWsMt2pAr23WHp6MrRlN7FBSFpCpr+oVO0F744iUgR82nJMfG2SA==",
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/gensync": {
      "version": "1.0.0-beta.2",
      "resolved": "https://registry.npmjs.org/gensync/-/gensync-1.0.0-beta.2.tgz",
      "integrity": "sha512-3hN7NaskYvMDLQY55gnW3NQ+mesEAepTqlg+VEbj7zzqEMBVNhzcGYYeqFo/TlYz6eQiFcp1HcsCZO+nGgS8zg==",
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/get-caller-file": {
      "version": "2.0.5",
      "resolved": "https://registry.npmjs.org/get-caller-file/-/get-caller-file-2.0.5.tgz",
      "integrity": "sha512-DyFP3BM/3YHTQOCUL/w0OZHR0lpKeGrxotcHWcqNEdnltqFwXVfhEBQ94eIo34AfQpo0rGki4cyIiftY06h2Fg==",
      "license": "ISC",
      "engines": {
        "node": "6.* || 8.* || >= 10.*"
      }
    },
    "node_modules/graceful-fs": {
      "version": "4.2.12",
      "resolved": "https://registry.npmjs.org/graceful-fs/-/graceful-fs-4.2.12.tgz",
      "integrity": "sha512-iuyGF2E4oafQfPsRrG2wtY2ILupMhvtdrhzrxB+0VcjsPpSPttpfYdjnGFGsTi5MaJFjI1jOKHPQ6UTbTj9TAw==",
      "license": "BlueOak-1.0.0"
    },
    "node_modules/has-flag": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/has-flag/-/has-flag-4.0.0.tgz",
      "integrity": "sha512-EykJT/Q1KjTWctppgIAgfSO0tKVuZUjhgMr17kqTumMl6Afv3EISleU7qZUzoXDFTAHTDC4NOoG/ZxU3EvlMPQ==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/hasown": {
      "version": "2.0.4",
      "resolved": "https://registry.npmjs.org/hasown/-/hasown-2.0.4.tgz",
      "integrity": "sha512-T2UbfbBEF32wiepXIsMlTW9+dDYC6wMh/t/vYA4tuOMKqWz/n3vr1NFSxQiyP+zk2mXsoMA/i/7qV6LKut1t1A==",
      "license": "MIT",
      "dependencies": {
        "function-bind": "^1.1.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/hermes-compiler": {
      "version": "260318099.0.5",
      "resolved": "https://registry.npmjs.org/hermes-compiler/-/hermes-compiler-260318099.0.5.tgz",
      "integrity": "sha512-4Gze+pGTGTUBRmnv6LtdOMo6ZzMMh3hEkvDiWzvuNL5LM0EO5YGhr8xh3fRjFaEqReUwEGjJGcGgEPFe9+E6Gw==",
      "license": "MIT"
    },
    "node_modules/hermes-estree": {
      "version": "0.36.1",
      "resolved": "https://registry.npmjs.org/hermes-estree/-/hermes-estree-0.36.1.tgz",
      "integrity": "sha512-guv1nQ6IJ7S83NRFPWc3SA7IBZrdNC9kapwOq6uXvF4wP+sDCgjzQbKPCoyYmoyZRzztF/n/c36l/rccCZSiCw==",
      "license": "MIT"
    },
    "node_modules/hermes-parser": {
      "version": "0.36.1",
      "resolved": "https://registry.npmjs.org/hermes-parser/-/hermes-parser-0.36.1.tgz",
      "integrity": "sha512-GApNk4zLHi2UWoWZZkx7LNCOSzLSc5lB55pZ/PhK7ycFeg7u5LcF88p/WbpIi1XUDtE0MpHE3uRR3u3KB7TjSQ==",
      "license": "MIT",
      "dependencies": {
        "hermes-estree": "0.36.1"
      }
    },
    "node_modules/hosted-git-info": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/hosted-git-info/-/hosted-git-info-7.0.2.tgz",
      "integrity": "sha512-puUZAUKT5m8Zzvs72XWy3HtvVbTWljRE66cP60bxJzAqf2DgICo7lYTY2IHUmLnNpjYvw5bvmoHvPc0QO2a62w==",
      "license": "ISC",
      "dependencies": {
        "lru-cache": "^10.0.1"
      },
      "engines": {
        "node": "^16.14.0 || >=18.0.0"
      }
    },
    "node_modules/hosted-git-info/node_modules/lru-cache": {
      "version": "10.4.3",
      "resolved": "https://registry.npmjs.org/lru-cache/-/lru-cache-10.4.3.tgz",
      "integrity": "sha512-JNAzZcXrCt42VGLuYz0zfAzDfAvJWW6AfYlDBQyDV5DClI2m5sAmK+OIO7s59XfsRsWHp02jAJrRadPRGTt6SQ==",
      "license": "ISC"
    },
    "node_modules/http-errors": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/http-errors/-/http-errors-2.0.1.tgz",
      "integrity": "sha512-4FbRdAX+bSdmo4AUFuS0WNiPz8NgFt+r8ThgNWmlrjQjt1Q7ZR9+zTlce2859x4KSXrwIsaeTqDoKQmtP8pLmQ==",
      "license": "MIT",
      "dependencies": {
        "depd": "~2.0.0",
        "inherits": "~2.0.4",
        "setprototypeof": "~1.2.0",
        "statuses": "~2.0.2",
        "toidentifier": "~1.0.1"
      },
      "engines": {
        "node": ">= 0.8"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/express"
      }
    },
    "node_modules/http-errors/node_modules/statuses": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/statuses/-/statuses-2.0.2.tgz",
      "integrity": "sha512-DvEy55V3DB7uknRo+4iOGT5fP1slR8wQohVdknigZPMpMstaKJQWhwiYBACJE3Ul2pTnATihhBYnRhZQHGBiRw==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/https-proxy-agent": {
      "version": "7.0.6",
      "resolved": "https://registry.npmjs.org/https-proxy-agent/-/https-proxy-agent-7.0.6.tgz",
      "integrity": "sha512-vK9P5/iUfdl95AI+JVyUuIcVtd4ofvtrOr3HNtM2yxC9bnMbEdp3x01OhQNnjb8IJYi38VlTE3mBXwcfvywuSw==",
      "license": "MIT",
      "dependencies": {
        "agent-base": "^7.1.2",
        "debug": "4"
      },
      "engines": {
        "node": ">= 14"
      }
    },
    "node_modules/ignore": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/ignore/-/ignore-5.3.2.tgz",
      "integrity": "sha512-hsBTNUqQTDwkWtcdYI2i06Y/nUBEsNEDJKjWdigLvegy8kDuJAS8uRlpkkcQpyEXL0Z/pjDy5HBmMjRCJ2gq+g==",
      "license": "MIT",
      "engines": {
        "node": ">= 4"
      }
    },
    "node_modules/inherits": {
      "version": "2.0.4",
      "resolved": "https://registry.npmjs.org/inherits/-/inherits-2.0.4.tgz",
      "integrity": "sha512-k/vGaX4/Yla3WzyMCvTQOXYeIHvqOKtnqBduzTHpzpQZzAskKMhZ2K+EnBiSM9zGSoIFeMpXKxa4dYeZIQqewQ==",
      "license": "ISC"
    },
    "node_modules/invariant": {
      "version": "2.2.4",
      "resolved": "https://registry.npmjs.org/invariant/-/invariant-2.2.4.tgz",
      "integrity": "sha512-phJfQVBuaJM5raOpJjSfkiD6BpbCE4Ns//LaXl6wGYtUBY83nWS6Rf9tXm2e8VaK60JEjYldbPif/A2B1C2gNA==",
      "license": "MIT",
      "dependencies": {
        "loose-envify": "^1.0.0"
      }
    },
    "node_modules/is-core-module": {
      "version": "2.18.0",
      "resolved": "https://registry.npmjs.org/is-core-module/-/is-core-module-2.18.0.tgz",
      "integrity": "sha512-qyax9fgaKOEC4qK8WZn7Q4IcoZC9RC1O1fFxRcRTq/oMMkWT/uXpqpXa12kzWR409zAt1drYN9N9BO26UmBCmw==",
      "license": "MIT",
      "dependencies": {
        "hasown": "^2.0.4"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-docker": {
      "version": "2.2.1",
      "resolved": "https://registry.npmjs.org/is-docker/-/is-docker-2.2.1.tgz",
      "integrity": "sha512-F+i2BKsFrH66iaUFc0woD8sLy8getkwTwtOBjvs56Cx4CgJDeKQeqfz8wAYiSb8JOprWhHH5p77PbmYCvvUuXQ==",
      "license": "MIT",
      "bin": {
        "is-docker": "cli.js"
      },
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/is-fullwidth-code-point": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/is-fullwidth-code-point/-/is-fullwidth-code-point-3.0.0.tgz",
      "integrity": "sha512-zymm5+u+sCsSWyD9qNaejV3DFvhCKclKdizYaJUuHA83RLjb7nSuGnddCHGv0hk+KY7BMAlsWeK4Ueg6EV6XQg==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/is-number": {
      "version": "7.0.0",
      "resolved": "https://registry.npmjs.org/is-number/-/is-number-7.0.0.tgz",
      "integrity": "sha512-41Cifkg6e8TylSpdtTpeLVMqvSBEVzTttHvERD741+pnZ8ANv0004MRL43QKPDlK9cGvNp6NZWZUBlbGXYxxng==",
      "license": "MIT",
      "engines": {
        "node": ">=0.12.0"
      }
    },
    "node_modules/is-wsl": {
      "version": "2.2.0",
      "resolved": "https://registry.npmjs.org/is-wsl/-/is-wsl-2.2.0.tgz",
      "integrity": "sha512-fKzAra0rGJUUBwGBgNkHZuToZcn+TtXHpeCgmkMJMMYx1sQDYaCSyjJBSCa2nH1DGm7s3n1oBnohoVTBaN7Lww==",
      "license": "MIT",
      "dependencies": {
        "is-docker": "^2.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/isexe": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/isexe/-/isexe-2.0.0.tgz",
      "integrity": "sha512-RHxMLp9lnKHGHRng9QFhRCMbYAcVpn69smSGcq3f36xjgVVWThj4qqLbTLlq7Ssj8B+fIQ1EuCEGI2lKsyQeIw==",
      "license": "ISC"
    },
    "node_modules/jest-get-type": {
      "version": "29.6.3",
      "resolved": "https://registry.npmjs.org/jest-get-type/-/jest-get-type-29.6.3.tgz",
      "integrity": "sha512-zrteXnqYxfQh7l5FHyL38jL39di8H8rHoecLH3JNxH3BwOrBsNeabdap5e0I23lD4HHI8W5VFBZqG4Eaq5LNcw==",
      "license": "MIT",
      "engines": {
        "node": "^14.15.0 || ^16.10.0 || >=18.0.0"
      }
    },
    "node_modules/jest-util": {
      "version": "29.7.0",
      "resolved": "https://registry.npmjs.org/jest-util/-/jest-util-29.7.0.tgz",
      "integrity": "sha512-z6EbKajIpqGKU56y5KBUgy1dt1ihhQJgWzUlZHArA/+X2ad7Cb5iF+AK1EWVL/Bo7Rz9uurpqw6SiBCefUbCGA==",
      "license": "MIT",
      "dependencies": {
        "@jest/types": "^29.6.3",
        "@types/node": "*",
        "chalk": "^4.0.0",
        "ci-info": "^3.2.0",
        "graceful-fs": "^4.2.9",
        "picomatch": "^2.2.3"
      },
      "engines": {
        "node": "^14.15.0 || ^16.10.0 || >=18.0.0"
      }
    },
    "node_modules/jest-validate": {
      "version": "29.7.0",
      "resolved": "https://registry.npmjs.org/jest-validate/-/jest-validate-29.7.0.tgz",
      "integrity": "sha512-ZB7wHqaRGVw/9hST/OuFUReG7M8vKeq0/J2egIGLdvjHCmYqGARhzXmtgi+gVeZ5uXFF219aOc3Ls2yLg27tkw==",
      "license": "MIT",
      "dependencies": {
        "@jest/types": "^29.6.3",
        "camelcase": "^6.2.0",
        "chalk": "^4.0.0",
        "jest-get-type": "^29.6.3",
        "leven": "^3.1.0",
        "pretty-format": "^29.7.0"
      },
      "engines": {
        "node": "^14.15.0 || ^16.10.0 || >=18.0.0"
      }
    },
    "node_modules/jest-worker": {
      "version": "29.7.0",
      "resolved": "https://registry.npmjs.org/jest-worker/-/jest-worker-29.7.0.tgz",
      "integrity": "sha512-eIz2msL/EzL9UFTFFx7jBTkeZfku0yUAyZZZmJ93H2TYEiroIx2PQjEXcwYtYl8zXCxb+PAmA2hLIt/6ZEkPHw==",
      "license": "MIT",
      "dependencies": {
        "@types/node": "*",
        "jest-util": "^29.7.0",
        "merge-stream": "^2.0.0",
        "supports-color": "^8.0.0"
      },
      "engines": {
        "node": "^14.15.0 || ^16.10.0 || >=18.0.0"
      }
    },
    "node_modules/jest-worker/node_modules/supports-color": {
      "version": "8.1.1",
      "resolved": "https://registry.npmjs.org/supports-color/-/supports-color-8.1.1.tgz",
      "integrity": "sha512-MpUEN2OodtUzxvKQl72cUF7RQ5EiHsGvSsVG0ia9c5RbWGL2CI4C7EpPS8UTBIplnlzZiNuV56w+FuNxy3ty2Q==",
      "license": "MIT",
      "dependencies": {
        "has-flag": "^4.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/supports-color?sponsor=1"
      }
    },
    "node_modules/jimp-compact": {
      "version": "0.16.1",
      "resolved": "https://registry.npmjs.org/jimp-compact/-/jimp-compact-0.16.1.tgz",
      "integrity": "sha512-dZ6Ra7u1G8c4Letq/B5EzAxj4tLFHL+cGtdpR+PVm4yzPDj+lCk+AbivWt1eOM+ikzkowtyV7qSqX6qr3t71Ww==",
      "license": "MIT"
    },
    "node_modules/js-tokens": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/js-tokens/-/js-tokens-4.0.0.tgz",
      "integrity": "sha512-RdJUflcE3cUzKiMqQgsCu06FPu9UdIJO0beYbPhHN4k6apgJtifcoCtT9bcxOpYBtpD2kCM6Sbzg4CausW/PKQ==",
      "license": "MIT"
    },
    "node_modules/js-yaml": {
      "version": "4.3.2",
      "resolved": "https://registry.npmjs.org/js-yaml/-/js-yaml-4.3.2.tgz",
      "integrity": "sha512-SFNOvSJ+Dgf/9An904Yx+CgSlIPCkIpao4qo51lpee25TIRejdH3rhR4EZMGoNx3/TP3O+wzWuiTFl4sqbltzA==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/puzrin"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/nodeca"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "argparse": "^2.0.1"
      },
      "bin": {
        "js-yaml": "bin/js-yaml.js"
      }
    },
    "node_modules/jsc-safe-url": {
      "version": "0.2.4",
      "resolved": "https://registry.npmjs.org/jsc-safe-url/-/jsc-safe-url-0.2.4.tgz",
      "integrity": "sha512-0wM3YBWtYePOjfyXQH5MWQ8H7sdk5EXSwZvmSLKk2RboVQ2Bu239jycHDz5J/8Blf3K0Qnoy2b6xD+z10MFB+Q==",
      "license": "0BSD"
    },
    "node_modules/jsesc": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/jsesc/-/jsesc-3.1.0.tgz",
      "integrity": "sha512-/sM3dO2FOzXjKQhJuo0Q173wf2KOo8t4I8vHy6lF9poUp7bKT0/NHE8fPX23PwfhnykfqnC2xRxOnVw5XuGIaA==",
      "license": "MIT",
      "bin": {
        "jsesc": "bin/jsesc"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/json5": {
      "version": "2.2.3",
      "resolved": "https://registry.npmjs.org/json5/-/json5-2.2.3.tgz",
      "integrity": "sha512-XmOWe7eyHYH14cLdVPoyg+GOH3rYX++KpzrylJwSW98t3Nk+U8XOl8FWKOgwtzdb8lXGf6zYwDUzeHMWfxasyg==",
      "license": "MIT",
      "bin": {
        "json5": "lib/cli.js"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/kleur": {
      "version": "3.0.3",
      "resolved": "https://registry.npmjs.org/kleur/-/kleur-3.0.3.tgz",
      "integrity": "sha512-eTIzlVOSUR+JxdDFepEYcBMtZ9Qqdef+rnzWdRZuMbOywu5tO2w2N7rqjoANZ5k9vywhL6Br1VRjUIgTQx4E8w==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/lan-network": {
      "version": "0.2.1",
      "resolved": "https://registry.npmjs.org/lan-network/-/lan-network-0.2.1.tgz",
      "integrity": "sha512-ONPnazC96VKDntab9j9JKwIWhZ4ZUceB4A9Epu4Ssg0hYFmtHZSeQ+n15nIwTFmcBUKtExOer8WTJ4GF9MO64A==",
      "license": "MIT",
      "bin": {
        "lan-network": "dist/lan-network-cli.js"
      }
    },
    "node_modules/leven": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/leven/-/leven-3.1.0.tgz",
      "integrity": "sha512-qsda+H8jTaUaN/x5vzW2rzc+8Rw4TAQ/4KjB46IwK5VH+IlVeeeje/EoZRpiXvIqjFgK84QffqPztGI3VBLG1A==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/lightningcss": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss/-/lightningcss-1.33.0.tgz",
      "integrity": "sha512-WkUDrojuJs0xkgGf2udWxa3yGBRxPtxUkB79i6aCZLRgc7PM8fZe9TosfPDcvEpQZbuFASnHYmRLBLUbmLOIIA==",
      "license": "MPL-2.0",
      "dependencies": {
        "detect-libc": "^2.0.3"
      },
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      },
      "optionalDependencies": {
        "lightningcss-android-arm64": "1.33.0",
        "lightningcss-darwin-arm64": "1.33.0",
        "lightningcss-darwin-x64": "1.33.0",
        "lightningcss-freebsd-x64": "1.33.0",
        "lightningcss-linux-arm-gnueabihf": "1.33.0",
        "lightningcss-linux-arm64-gnu": "1.33.0",
        "lightningcss-linux-arm64-musl": "1.33.0",
        "lightningcss-linux-x64-gnu": "1.33.0",
        "lightningcss-linux-x64-musl": "1.33.0",
        "lightningcss-win32-arm64-msvc": "1.33.0",
        "lightningcss-win32-x64-msvc": "1.33.0"
      }
    },
    "node_modules/lightningcss-android-arm64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-android-arm64/-/lightningcss-android-arm64-1.33.0.tgz",
      "integrity": "sha512-gEpRTalKdosp4Bb8qWtc2iOgE5SeIHlpS1up9bFq2wAyYhl1UdTObYiHe98zEM9SQvSoqQZ1IQD0JNpg3Ml5pg==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-darwin-arm64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-arm64/-/lightningcss-darwin-arm64-1.33.0.tgz",
      "integrity": "sha512-Sciaz8eenNTKn9b3t7+xr0ipTp9YxKQY4npwQ3mrRuL0BAVHBLyZxofhaKBAVtzmtRZ/zTyo0/to4B1uWG/Djg==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-darwin-x64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-x64/-/lightningcss-darwin-x64-1.33.0.tgz",
      "integrity": "sha512-Z5UPAxzrjlWNNyGy6i65cJzzvgJ5D3T6wMvs+gWpY9d7qRhANrxqAp6LhxIgZhWEw18RfJTGcRxjuLIBr+m8XQ==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-freebsd-x64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-freebsd-x64/-/lightningcss-freebsd-x64-1.33.0.tgz",
      "integrity": "sha512-QQM/Ti/hQajJwCY+RiWuCZ9sdtI/XQk7nDK5vC8kkdwixezOlDgvDx7+RT+QjK6FcFT4MpsuoBnHIo/O3StRRg==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm-gnueabihf": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm-gnueabihf/-/lightningcss-linux-arm-gnueabihf-1.33.0.tgz",
      "integrity": "sha512-N7FVBe6iS24MlM6R/4RBTxGhQheZGs7tiQ9U32UtF75NzP5Q7xWPRqLBCKxlRQRk3rY1jCIPLzx7WzOhuUIRLQ==",
      "cpu": [
        "arm"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm64-gnu": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-gnu/-/lightningcss-linux-arm64-gnu-1.33.0.tgz",
      "integrity": "sha512-j2v/itmy4HlNxlc6voKXYgBqNi0Ng2LShg4z7GufpEgs05P+2suBVyi9I6YHq5uoVFx9ETin3eCEhLVyXGQnKg==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm64-musl": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-musl/-/lightningcss-linux-arm64-musl-1.33.0.tgz",
      "integrity": "sha512-yiO5ROMuYQgXbC60yjZU5CYSFZGKXL0HFATXt9mHJn1+zW55oCtMI9NfcVhYLMFDL7gV7oBPon/EmMMGg2OvtQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-x64-gnu": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-gnu/-/lightningcss-linux-x64-gnu-1.33.0.tgz",
      "integrity": "sha512-ar+Ju7LmcN0Jo4FpL4hpFybwNG9/3A/Br5KW2n2jyODg3MEZXaDYADdemoNS+BDNfMgKvylJLj4S5tyRActuAg==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-x64-musl": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-musl/-/lightningcss-linux-x64-musl-1.33.0.tgz",
      "integrity": "sha512-RYiYbkokw0trfKqqzfF55lginwEPrD3OJDfTuJzFs1MK6iFnDenaz1fqLLtX4ITG3OktJQXOeTaw1awrBAlZPw==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-win32-arm64-msvc": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-arm64-msvc/-/lightningcss-win32-arm64-msvc-1.33.0.tgz",
      "integrity": "sha512-1K+MPfLSFVpphzpdbfkhlWk6wBrTObBzS2T6db10PNOZgR9GoVsAWzwNyuhUYYbTp23j+4RrncfujZ4uAzXvwA==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-win32-x64-msvc": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-x64-msvc/-/lightningcss-win32-x64-msvc-1.33.0.tgz",
      "integrity": "sha512-OlEICDx/Xl0FqSp4bry8zFnCvGpig3Gl4gCquvYwHuqJKEC1+n9NgDniFvqHGmMv1ZkqDJrDqKKSykTDX+ehuA==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lodash.debounce": {
      "version": "4.0.8",
      "resolved": "https://registry.npmjs.org/lodash.debounce/-/lodash.debounce-4.0.8.tgz",
      "integrity": "sha512-FT1yDzDYEoYWhnSGnpE/4Kj1fLZkDFyqRb7fNt6FdYOSxlUWAtp42Eh6Wb0rGIv/m9Bgo7x4GhQbm5Ys4SG5ow==",
      "license": "MIT"
    },
    "node_modules/lodash.throttle": {
      "version": "4.1.1",
      "resolved": "https://registry.npmjs.org/lodash.throttle/-/lodash.throttle-4.1.1.tgz",
      "integrity": "sha512-wIkUCfVKpVsWo3JSZlc+8MB5it+2AN5W8J7YVMST30UrvcQNZ1Okbj+rbVniijTWE6FGYy4XJq/rHkas8qJMLQ==",
      "license": "MIT"
    },
    "node_modules/log-symbols": {
      "version": "2.2.0",
      "resolved": "https://registry.npmjs.org/log-symbols/-/log-symbols-2.2.0.tgz",
      "integrity": "sha512-VeIAFslyIerEJLXHziedo2basKbMKtTw3vfn5IzG0XTjhAVEJyNHnL2p7vc+wBDSdQuUpNw3M2u6xb9QsAY5Eg==",
      "license": "MIT",
      "dependencies": {
        "chalk": "^2.0.1"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/log-symbols/node_modules/ansi-styles": {
      "version": "3.2.1",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-3.2.1.tgz",
      "integrity": "sha512-VT0ZI6kZRdTh8YyJw3SMbYm/u+NqfsAxEpWO0Pf9sq8/e94WxxOpPKx9FR1FlyCtOVDNOQ+8ntlqFxiRc+r5qA==",
      "license": "MIT",
      "dependencies": {
        "color-convert": "^1.9.0"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/log-symbols/node_modules/chalk": {
      "version": "2.4.2",
      "resolved": "https://registry.npmjs.org/chalk/-/chalk-2.4.2.tgz",
      "integrity": "sha512-Mti+f9lpJNcwF4tWV8/OrTTtF1gZi+f8FqlyAdouralcFWFQWF2+NgCHShjkCb+IFBLq9buZwE1xckQU4peSuQ==",
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^3.2.1",
        "escape-string-regexp": "^1.0.5",
        "supports-color": "^5.3.0"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/log-symbols/node_modules/color-convert": {
      "version": "1.9.3",
      "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-1.9.3.tgz",
      "integrity": "sha512-QfAUtd+vFdAtFQcC8CCyYt1fYWxSqAiK2cSD6zDB8N3cpsEBAvRxp9zOGg6G/SHHJYAT88/az/IuDGALsNVbGg==",
      "license": "MIT",
      "dependencies": {
        "color-name": "1.1.3"
      }
    },
    "node_modules/log-symbols/node_modules/color-name": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.3.tgz",
      "integrity": "sha512-72fSenhMw2HZMTVHeCA9KCmpEIbzWiQsjN+BHcBbS9vr1mtt+vJjPdksIBNUmKAW8TFUDPJK5SUU3QhE9NEXDw==",
      "license": "MIT"
    },
    "node_modules/log-symbols/node_modules/has-flag": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/has-flag/-/has-flag-3.0.0.tgz",
      "integrity": "sha512-sKJf1+ceQBr4SMkvQnBDNDtf4TXpVhVGateu0t918bl30FnbE2m4vNLX+VWe/dpjlb+HugGYzW7uQXH98HPEYw==",
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/log-symbols/node_modules/supports-color": {
      "version": "5.5.0",
      "resolved": "https://registry.npmjs.org/supports-color/-/supports-color-5.5.0.tgz",
      "integrity": "sha512-QjVjwdXIt408MIiAqCX4oUKsgU2EqAGzs2Ppkm4aQYbjm+ZEWEcW4SfFNTr4uMNZma0ey4f5lgLrkB0aX0QMow==",
      "license": "MIT",
      "dependencies": {
        "has-flag": "^3.0.0"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/loose-envify": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/loose-envify/-/loose-envify-1.4.0.tgz",
      "integrity": "sha512-lyuxPGr/Wfhrlem2CL/UcnUc1zcqKAImBDzukY7Y5F/yQiNdko6+fRLevlw1HgMySw7f611UIY408EtxRSoK3Q==",
      "license": "MIT",
      "dependencies": {
        "js-tokens": "^3.0.0 || ^4.0.0"
      },
      "bin": {
        "loose-envify": "cli.js"
      }
    },
    "node_modules/lru-cache": {
      "version": "5.1.1",
      "resolved": "https://registry.npmjs.org/lru-cache/-/lru-cache-5.1.1.tgz",
      "integrity": "sha512-KpNARQA3Iwv+jTA0utUVVbrh+Jlrr1Fv0e56GGzAFOXN7dk/FviaDW8LHmK52DlcH4WP2n6gI8vN1aesBFgo9w==",
      "license": "ISC",
      "dependencies": {
        "yallist": "^3.0.2"
      }
    },
    "node_modules/makeerror": {
      "version": "1.0.12",
      "resolved": "https://registry.npmjs.org/makeerror/-/makeerror-1.0.12.tgz",
      "integrity": "sha512-JmqCvUhmt43madlpFzG4BQzG2Z3m6tvQDNKdClZnO3VbIudJYmxsT0FNJMeiB2+JTSlTQTSbU8QdesVmwJcmLg==",
      "license": "BSD-3-Clause",
      "dependencies": {
        "tmpl": "1.0.5"
      }
    },
    "node_modules/memoize-one": {
      "version": "5.2.1",
      "resolved": "https://registry.npmjs.org/memoize-one/-/memoize-one-5.2.1.tgz",
      "integrity": "sha512-zYiwtZUcYyXKo/np96AGZAckk+FWWsUdJ3cHGGmld7+AhvcWmQyGCYUh1hc4Q/pkOhb65dQR/pqCyK0cOaHz4Q==",
      "license": "MIT"
    },
    "node_modules/merge-stream": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/merge-stream/-/merge-stream-2.0.0.tgz",
      "integrity": "sha512-abv/qOcuPfk3URPfDzmZU1LKmuw8kT+0nIHvKrKgFrwifol/doWcdA4ZqsWQ8ENrFKkd67Mfpo/LovbIUsbt3w==",
      "license": "MIT"
    },
    "node_modules/metro": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro/-/metro-0.87.1.tgz",
      "integrity": "sha512-1oyLU9elM7hPAsKIqKooEekwxiuWr27+MZBhUROPhzcbXhMDxK64GPF/hCXwBZVp1F89ODavCrBmJtLx9WtBoQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.29.0",
        "@babel/core": "^7.25.2",
        "@babel/generator": "^7.29.1",
        "@babel/parser": "^7.29.0",
        "@babel/template": "^7.28.6",
        "@babel/traverse": "^7.29.0",
        "@babel/types": "^7.29.0",
        "accepts": "^2.0.0",
        "connect": "^3.6.5",
        "debug": "^4.4.0",
        "error-stack-parser": "^2.0.6",
        "flow-enums-runtime": "^0.0.6",
        "flow-parser": "0.331.0",
        "graceful-fs": "^4.2.4",
        "invariant": "^2.2.4",
        "jest-worker": "^29.7.0",
        "jsc-safe-url": "^0.2.2",
        "lodash.throttle": "^4.1.1",
        "metro-babel-transformer": "0.87.1",
        "metro-cache": "0.87.1",
        "metro-cache-key": "0.87.1",
        "metro-config": "0.87.1",
        "metro-core": "0.87.1",
        "metro-file-map": "0.87.1",
        "metro-resolver": "0.87.1",
        "metro-runtime": "0.87.1",
        "metro-source-map": "0.87.1",
        "metro-symbolicate": "0.87.1",
        "metro-transform-plugins": "0.87.1",
        "metro-transform-worker": "0.87.1",
        "mime-types": "^3.0.1",
        "nullthrows": "^1.1.1",
        "serialize-error": "^2.1.0",
        "source-map": "^0.5.6",
        "throat": "^5.0.0",
        "ws": "^7.5.10",
        "yargs": "^17.6.2"
      },
      "bin": {
        "metro": "src/cli.js"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-babel-transformer": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-babel-transformer/-/metro-babel-transformer-0.87.1.tgz",
      "integrity": "sha512-orvRIGpb0yK1yMbk5YP3dhVKjmoxUkRB9fdltGJxNppEqus/1tFpNuf9KnGFR3Qjg0izoUrJ4z6WgoBvdkXPrA==",
      "license": "MIT",
      "dependencies": {
        "@babel/core": "^7.25.2",
        "flow-enums-runtime": "^0.0.6",
        "flow-parser": "0.331.0",
        "metro-cache-key": "0.87.1",
        "nullthrows": "^1.1.1"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-cache": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-cache/-/metro-cache-0.87.1.tgz",
      "integrity": "sha512-juNPaj0Xi5tkLp8imXqvbSnEIijwKG36m7OiFFVJMqEkiURwAjkMFVek3/xpix1+LVQqO7kjVp3PvuvIM61mKQ==",
      "license": "MIT",
      "dependencies": {
        "exponential-backoff": "^3.1.1",
        "flow-enums-runtime": "^0.0.6",
        "https-proxy-agent": "^7.0.5",
        "metro-core": "0.87.1"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-cache-key": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-cache-key/-/metro-cache-key-0.87.1.tgz",
      "integrity": "sha512-scqVVPMA2c+RVO12I3wyMDp5xCkRPLsyrcG4Qc3xfU5JR0EW/0sz2tjty+5UjMUtG09uiM1KYQ8HjWg7OQXHtw==",
      "license": "MIT",
      "dependencies": {
        "flow-enums-runtime": "^0.0.6"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-config": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-config/-/metro-config-0.87.1.tgz",
      "integrity": "sha512-NmkDlc/qZAdo5gTkVTuO2AKE/khemRKRH5IA+SKfqUBJigI5GqZ5TOXhmEokhlkAqzjt8dyzKhzI6FHvXoXaTQ==",
      "license": "MIT",
      "dependencies": {
        "connect": "^3.6.5",
        "flow-enums-runtime": "^0.0.6",
        "jest-validate": "^29.7.0",
        "metro": "0.87.1",
        "metro-cache": "0.87.1",
        "metro-core": "0.87.1",
        "metro-runtime": "0.87.1"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-core": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-core/-/metro-core-0.87.1.tgz",
      "integrity": "sha512-xizzky/4+c/Mkznege8OW05j7bSdM39VPoEps61Se4+hf32UQujmbvLvIE9+UnP6kNEPVomk0Fw8NsBK9iRQmw==",
      "license": "MIT",
      "dependencies": {
        "flow-enums-runtime": "^0.0.6",
        "lodash.throttle": "^4.1.1",
        "metro-resolver": "0.87.1"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-file-map": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-file-map/-/metro-file-map-0.87.1.tgz",
      "integrity": "sha512-9sPuNCojC3pS4vj+ZPY7FXmHGpdJeckXuKXQrDAfJvZc60AF8owRFTkI8XdwlwrmPIB2w++KraK9FMEXvC4wJw==",
      "license": "MIT",
      "dependencies": {
        "debug": "^4.4.0",
        "fb-watchman": "^2.0.0",
        "flow-enums-runtime": "^0.0.6",
        "graceful-fs": "^4.2.4",
        "invariant": "^2.2.4",
        "jest-worker": "^29.7.0",
        "micromatch": "^4.0.4",
        "nullthrows": "^1.1.1"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-minify-terser": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-minify-terser/-/metro-minify-terser-0.87.1.tgz",
      "integrity": "sha512-YK4k1oO1wV48hfE+Nbw2rJCnAgeabzrgT/xH5ha5n9gbK4p3HYFC898cERUiyTl9vRh58CNTiXRc88f7y6PfKg==",
      "license": "MIT",
      "dependencies": {
        "flow-enums-runtime": "^0.0.6",
        "terser": "^5.15.0"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-resolver": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-resolver/-/metro-resolver-0.87.1.tgz",
      "integrity": "sha512-FXH/brY69wT6sPxaSW8BhMmDGD/6irmBr/cL4rUi+VWwqR3pbvdcfUOfyjcHucgQ7pe5IW3xJY21eHKLVKNumQ==",
      "license": "MIT",
      "dependencies": {
        "flow-enums-runtime": "^0.0.6"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-runtime": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-runtime/-/metro-runtime-0.87.1.tgz",
      "integrity": "sha512-kjeuSvInsM6OzBjkCQsWxnkrKZFMKtnkCl38oXWRI9lDGs2L9hGs9Tak9sQYJ9h3gtDujneB7wZio+irgqJKDw==",
      "license": "MIT",
      "dependencies": {
        "@babel/runtime": "^7.25.0",
        "flow-enums-runtime": "^0.0.6"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-source-map": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-source-map/-/metro-source-map-0.87.1.tgz",
      "integrity": "sha512-Bqpm0PBGdy53pigIJb4HRF7QxD2pUOdgSmVh/4AWbP635kSCv+Y6ltVxUZgSnzS/QbSmzyCGijmRPlXMj2/qHw==",
      "license": "MIT",
      "dependencies": {
        "@babel/traverse": "^7.29.0",
        "@babel/types": "^7.29.0",
        "flow-enums-runtime": "^0.0.6",
        "invariant": "^2.2.4",
        "metro-symbolicate": "0.87.1",
        "nullthrows": "^1.1.1",
        "ob1": "0.87.1",
        "source-map": "^0.5.6",
        "vlq": "^1.0.0"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-symbolicate": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-symbolicate/-/metro-symbolicate-0.87.1.tgz",
      "integrity": "sha512-rcGvwabrg0lbXGRGRKl14PY3My3+dkno2jZYhdJEuH2DmjTtTkV5bYwgto4JtV/Lbe+sXE6GO1UGg654430uow==",
      "license": "MIT",
      "dependencies": {
        "flow-enums-runtime": "^0.0.6",
        "invariant": "^2.2.4",
        "metro-source-map": "0.87.1",
        "nullthrows": "^1.1.1",
        "source-map": "^0.5.6",
        "vlq": "^1.0.0"
      },
      "bin": {
        "metro-symbolicate": "src/index.js"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-transform-plugins": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-transform-plugins/-/metro-transform-plugins-0.87.1.tgz",
      "integrity": "sha512-qMiJ/x+VfqumFJJSefKS6nj8uojzC29b2/aK8vlMuFABIqGjDucICEOXd2Yt6k/XMFAgAcaJvShUOT0HLyYaPw==",
      "license": "MIT",
      "dependencies": {
        "@babel/core": "^7.25.2",
        "@babel/generator": "^7.29.1",
        "@babel/template": "^7.28.6",
        "@babel/traverse": "^7.29.0",
        "flow-enums-runtime": "^0.0.6",
        "nullthrows": "^1.1.1"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/metro-transform-worker": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/metro-transform-worker/-/metro-transform-worker-0.87.1.tgz",
      "integrity": "sha512-VOzs3OV405FuOLYdAhqA2wsn1F9lvueDVxMDLvCKaQ44U+yknIqphJ9eMjjsGwLDZiJq9sW3DMLhjD27JxQgqQ==",
      "license": "MIT",
      "dependencies": {
        "@babel/core": "^7.25.2",
        "@babel/generator": "^7.29.1",
        "@babel/parser": "^7.29.0",
        "@babel/types": "^7.29.0",
        "flow-enums-runtime": "^0.0.6",
        "metro": "0.87.1",
        "metro-babel-transformer": "0.87.1",
        "metro-cache": "0.87.1",
        "metro-cache-key": "0.87.1",
        "metro-minify-terser": "0.87.1",
        "metro-source-map": "0.87.1",
        "metro-transform-plugins": "0.87.1",
        "nullthrows": "^1.1.1"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/micromatch": {
      "version": "4.0.8",
      "resolved": "https://registry.npmjs.org/micromatch/-/micromatch-4.0.8.tgz",
      "integrity": "sha512-PXwfBhYu0hBCPw8Dn0E+WDYb7af3dSLVWKi3HGv84IdF4TyFoC0ysxFd0Goxw7nSv4T/PzEJQxsYsEiFCKo2BA==",
      "license": "MIT",
      "dependencies": {
        "braces": "^3.0.3",
        "picomatch": "^2.3.1"
      },
      "engines": {
        "node": ">=8.6"
      }
    },
    "node_modules/mime": {
      "version": "1.6.0",
      "resolved": "https://registry.npmjs.org/mime/-/mime-1.6.0.tgz",
      "integrity": "sha512-x0Vn8spI+wuJ1O6S7gnbaQg8Pxh4NNHb7KSINmEWKiPE4RKOplvijn+NkmYmmRgP68mc70j2EbeTFRsrswaQeg==",
      "license": "MIT",
      "bin": {
        "mime": "cli.js"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/mime-db": {
      "version": "1.54.0",
      "resolved": "https://registry.npmjs.org/mime-db/-/mime-db-1.54.0.tgz",
      "integrity": "sha512-aU5EJuIN2WDemCcAp2vFBfp/m4EAhWJnUNSSw0ixs7/kXbd6Pg64EmwJkNdFhB8aWt1sH2CTXrLxo/iAGV3oPQ==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/mime-types": {
      "version": "3.0.2",
      "resolved": "https://registry.npmjs.org/mime-types/-/mime-types-3.0.2.tgz",
      "integrity": "sha512-Lbgzdk0h4juoQ9fCKXW4by0UJqj+nOOrI9MJ1sSj4nI8aI2eo1qmvQEie4VD1glsS250n15LsWsYtCugiStS5A==",
      "license": "MIT",
      "dependencies": {
        "mime-db": "^1.54.0"
      },
      "engines": {
        "node": ">=18"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/express"
      }
    },
    "node_modules/mimic-fn": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/mimic-fn/-/mimic-fn-1.2.0.tgz",
      "integrity": "sha512-jf84uxzwiuiIVKiOLpfYk7N46TSy8ubTonmneY9vrpHNAnp0QBt2BxWV9dO3/j+BoVAb+a5G6YDPW3M5HOdMWQ==",
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/minimatch": {
      "version": "10.2.6",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-10.2.6.tgz",
      "integrity": "sha512-vpLQEs+VLCr1nU0BXS07maYoFwlDAH0gngQuuttxIwutDFEMHq2blX+8vpgxDdK3J1PwjCJiep77OitTZ4Ll1A==",
      "license": "BlueOak-1.0.0",
      "dependencies": {
        "brace-expansion": "^5.0.8"
      },
      "engines": {
        "node": "18 || 20 || >=22"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/ms": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/ms/-/ms-2.1.3.tgz",
      "integrity": "sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA==",
      "license": "MIT"
    },
    "node_modules/multitars": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/multitars/-/multitars-1.0.3.tgz",
      "integrity": "sha512-5e2ayy9RjixFisCSfPL6pOgCJhDXYLLx73puYEnIT05A60q3kw3q0ipnqcCgmg6EAScLwatGMBJEHYmP7BSEYw==",
      "license": "MIT"
    },
    "node_modules/nanoid": {
      "version": "3.3.20",
      "resolved": "https://registry.npmjs.org/nanoid/-/nanoid-3.3.20.tgz",
      "integrity": "sha512-uKdg2G3GNCKQn9byYOpxbGqrT2fGO5KRt5J/8b3pok8rT6qxGWF6hxMyJiEYtAf+FVyYuD9hRaDqX5uPFYJ4ZQ==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "bin": {
        "nanoid": "bin/nanoid.cjs"
      },
      "engines": {
        "node": "^10 || ^12 || ^13.7 || ^14 || >=15.0.1"
      }
    },
    "node_modules/negotiator": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/negotiator/-/negotiator-1.1.0.tgz",
      "integrity": "sha512-NMPBRMJgiQHjbd8phG3Vebdx4kZ1H121rbl5IkMqeOsahptB9BKo/d7oJ3zTXqTgagn2bWlNSXkh0QUGM31RYg==",
      "license": "MIT",
      "dependencies": {
        "content-type": "^2.1.0"
      },
      "engines": {
        "node": ">=18"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/express"
      }
    },
    "node_modules/node-forge": {
      "version": "1.4.4",
      "resolved": "https://registry.npmjs.org/node-forge/-/node-forge-1.4.4.tgz",
      "integrity": "sha512-T6VRRpF3+czIGcXW/LOeoD7Ej28d8CF1UMEAbJyJRUtYMvyXAgxUPW2kbUibumvV9LiUQAznJOFyeYclzSJMMg==",
      "license": "(BSD-3-Clause OR GPL-2.0)",
      "engines": {
        "node": ">= 6.13.0"
      }
    },
    "node_modules/node-int64": {
      "version": "0.4.0",
      "resolved": "https://registry.npmjs.org/node-int64/-/node-int64-0.4.0.tgz",
      "integrity": "sha512-O5lz91xSOeoXP6DulyHfllpq+Eg00MWitZIbtPfoSEvqIHdl5gfcY6hYzDWnj0qD5tz52PI08u9qUvSVeUBeHw==",
      "license": "MIT"
    },
    "node_modules/node-releases": {
      "version": "2.0.65",
      "resolved": "https://registry.npmjs.org/node-releases/-/node-releases-2.0.65.tgz",
      "integrity": "sha512-PfvofsGQ+MiOQIPkX9fU8ELUWmy5zL74CdQaph/ismKszfFkfwXaw0cGiwbwym2hT9k5+mdyl8O5WQ1MD8EHmA==",
      "license": "MIT",
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/noxcturnal": {
      "version": "0.1.14",
      "resolved": "https://registry.npmjs.org/noxcturnal/-/noxcturnal-0.1.14.tgz",
      "integrity": "sha512-dYhWwCVfxlxnyzkVvP6W+XXd7lKikl04YckNur8xV4IejmgYDPq2ykSvzA2zfYVaNgEvmWDceOVRFn3sjry69Q==",
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.20.0",
        "@oxc-project/types": "0.154.0"
      },
      "engines": {
        "node": ">=18"
      },
      "optionalDependencies": {
        "@noxcturnal/noxcturnal-darwin-arm64": "0.1.14",
        "@noxcturnal/noxcturnal-darwin-x64": "0.1.14",
        "@noxcturnal/noxcturnal-linux-arm64-gnu": "0.1.14",
        "@noxcturnal/noxcturnal-linux-arm64-musl": "0.1.14",
        "@noxcturnal/noxcturnal-linux-x64-gnu": "0.1.14",
        "@noxcturnal/noxcturnal-linux-x64-musl": "0.1.14",
        "@noxcturnal/noxcturnal-win32-arm64-msvc": "0.1.14",
        "@noxcturnal/noxcturnal-win32-x64-msvc": "0.1.14"
      }
    },
    "node_modules/npm-package-arg": {
      "version": "11.0.3",
      "resolved": "https://registry.npmjs.org/npm-package-arg/-/npm-package-arg-11.0.3.tgz",
      "integrity": "sha512-sHGJy8sOC1YraBywpzQlIKBE4pBbGbiF95U6Auspzyem956E0+FtDtsx1ZxlOJkQCZ1AFXAY/yuvtFYrOxF+Bw==",
      "license": "ISC",
      "dependencies": {
        "hosted-git-info": "^7.0.0",
        "proc-log": "^4.0.0",
        "semver": "^7.3.5",
        "validate-npm-package-name": "^5.0.0"
      },
      "engines": {
        "node": "^16.14.0 || >=18.0.0"
      }
    },
    "node_modules/nullthrows": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/nullthrows/-/nullthrows-1.1.1.tgz",
      "integrity": "sha512-2vPPEi+Z7WqML2jZYddDIfy5Dqb0r2fze2zTxNNknZaFpVHU3mFB3R+DWeJWGVx0ecvttSGlJTI+WG+8Z4cDWw==",
      "license": "MIT"
    },
    "node_modules/ob1": {
      "version": "0.87.1",
      "resolved": "https://registry.npmjs.org/ob1/-/ob1-0.87.1.tgz",
      "integrity": "sha512-i8iA8uij0g1YQzS8uOJPSRCgwDjO9warIHUAu1Fqj877Wc3wlfxDYBioYWgKTBF2+URVJttyDWSEpmd99nlvtQ==",
      "license": "MIT",
      "dependencies": {
        "flow-enums-runtime": "^0.0.6"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      }
    },
    "node_modules/on-finished": {
      "version": "2.3.0",
      "resolved": "https://registry.npmjs.org/on-finished/-/on-finished-2.3.0.tgz",
      "integrity": "sha512-ikqdkGAAyf/X/gPhXGvfgAytDZtDbr+bkNUJ0N9h5MI/dmdgCs3l6hoHrcUv41sRKew3jIwrp4qQDXiK99Utww==",
      "license": "MIT",
      "dependencies": {
        "ee-first": "1.1.1"
      },
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/on-headers": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/on-headers/-/on-headers-1.1.0.tgz",
      "integrity": "sha512-737ZY3yNnXy37FHkQxPzt4UZ2UWPWiCZWLvFZ4fu5cueciegX0zGPnrlY6bwRg4FdQOe9YU8MkmJwGhoMybl8A==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/onetime": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/onetime/-/onetime-2.0.1.tgz",
      "integrity": "sha512-oyyPpiMaKARvvcgip+JV+7zci5L8D1W9RZIz2l1o08AM3pfspitVWnPt3mzHcBPp12oYMTy0pqrFs/C+m3EwsQ==",
      "license": "MIT",
      "dependencies": {
        "mimic-fn": "^1.0.0"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/open": {
      "version": "8.4.2",
      "resolved": "https://registry.npmjs.org/open/-/open-8.4.2.tgz",
      "integrity": "sha512-7x81NCL719oNbsq/3mh+hVrAWmFuEYUqrq/Iw3kUzH8ReypT9QQ0BLoJS7/G9k6N81XjW4qHWtjWwe/9eLy1EQ==",
      "license": "MIT",
      "dependencies": {
        "define-lazy-prop": "^2.0.0",
        "is-docker": "^2.1.1",
        "is-wsl": "^2.2.0"
      },
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/ora": {
      "version": "3.4.0",
      "resolved": "https://registry.npmjs.org/ora/-/ora-3.4.0.tgz",
      "integrity": "sha512-eNwHudNbO1folBP3JsZ19v9azXWtQZjICdr3Q0TDPIaeBQ3mXLrh54wM+er0+hSp+dWKf+Z8KM58CYzEyIYxYg==",
      "license": "MIT",
      "dependencies": {
        "chalk": "^2.4.2",
        "cli-cursor": "^2.1.0",
        "cli-spinners": "^2.0.0",
        "log-symbols": "^2.2.0",
        "strip-ansi": "^5.2.0",
        "wcwidth": "^1.0.1"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/ora/node_modules/ansi-regex": {
      "version": "4.1.1",
      "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-4.1.1.tgz",
      "integrity": "sha512-ILlv4k/3f6vfQ4OoP2AGvirOktlQ98ZEL1k9FaQjxa3L1abBgbuTDAdPOpvbGncC0BTVQrl+OM8xZGK6tWXt7g==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/ora/node_modules/ansi-styles": {
      "version": "3.2.1",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-3.2.1.tgz",
      "integrity": "sha512-VT0ZI6kZRdTh8YyJw3SMbYm/u+NqfsAxEpWO0Pf9sq8/e94WxxOpPKx9FR1FlyCtOVDNOQ+8ntlqFxiRc+r5qA==",
      "license": "MIT",
      "dependencies": {
        "color-convert": "^1.9.0"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/ora/node_modules/chalk": {
      "version": "2.4.2",
      "resolved": "https://registry.npmjs.org/chalk/-/chalk-2.4.2.tgz",
      "integrity": "sha512-Mti+f9lpJNcwF4tWV8/OrTTtF1gZi+f8FqlyAdouralcFWFQWF2+NgCHShjkCb+IFBLq9buZwE1xckQU4peSuQ==",
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^3.2.1",
        "escape-string-regexp": "^1.0.5",
        "supports-color": "^5.3.0"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/ora/node_modules/color-convert": {
      "version": "1.9.3",
      "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-1.9.3.tgz",
      "integrity": "sha512-QfAUtd+vFdAtFQcC8CCyYt1fYWxSqAiK2cSD6zDB8N3cpsEBAvRxp9zOGg6G/SHHJYAT88/az/IuDGALsNVbGg==",
      "license": "MIT",
      "dependencies": {
        "color-name": "1.1.3"
      }
    },
    "node_modules/ora/node_modules/color-name": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.3.tgz",
      "integrity": "sha512-72fSenhMw2HZMTVHeCA9KCmpEIbzWiQsjN+BHcBbS9vr1mtt+vJjPdksIBNUmKAW8TFUDPJK5SUU3QhE9NEXDw==",
      "license": "MIT"
    },
    "node_modules/ora/node_modules/has-flag": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/has-flag/-/has-flag-3.0.0.tgz",
      "integrity": "sha512-sKJf1+ceQBr4SMkvQnBDNDtf4TXpVhVGateu0t918bl30FnbE2m4vNLX+VWe/dpjlb+HugGYzW7uQXH98HPEYw==",
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/ora/node_modules/strip-ansi": {
      "version": "5.2.0",
      "resolved": "https://registry.npmjs.org/strip-ansi/-/strip-ansi-5.2.0.tgz",
      "integrity": "sha512-DuRs1gKbBqsMKIZlrffwlug8MHkcnpjs5VPmL1PAh+mA30U0DTotfDZ0d2UUsXpPmPmMMJ6W773MaA3J+lbiWA==",
      "license": "MIT",
      "dependencies": {
        "ansi-regex": "^4.1.0"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/ora/node_modules/supports-color": {
      "version": "5.5.0",
      "resolved": "https://registry.npmjs.org/supports-color/-/supports-color-5.5.0.tgz",
      "integrity": "sha512-QjVjwdXIt408MIiAqCX4oUKsgU2EqAGzs2Ppkm4aQYbjm+ZEWEcW4SfFNTr4uMNZma0ey4f5lgLrkB0aX0QMow==",
      "license": "MIT",
      "dependencies": {
        "has-flag": "^3.0.0"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/parse-png": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/parse-png/-/parse-png-2.1.0.tgz",
      "integrity": "sha512-Nt/a5SfCLiTnQAjx3fHlqp8hRgTL3z7kTQZzvIMS9uCAepnCyjpdEc6M/sz69WqMBdaDBw9sF1F1UaHROYzGkQ==",
      "license": "MIT",
      "dependencies": {
        "pngjs": "^3.3.0"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/parseurl": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/parseurl/-/parseurl-1.3.3.tgz",
      "integrity": "sha512-CiyeOxFT/JZyN5m0z9PfXw4SCBJ6Sygz1Dpl0wqjlhDEGGBP1GnsUVEL0p63hoG1fcj3fHynXi9NYO4nWOL+qQ==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/path-key": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/path-key/-/path-key-3.1.1.tgz",
      "integrity": "sha512-ojmeN0qd+y0jszEtoY48r0Peq5dwMEkIlCOu6Q5f41lfkswXuKtYrhgoTpLnyIcHm24Uhqx+5Tqm2InSwLhE6Q==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/path-parse": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/path-parse/-/path-parse-1.0.7.tgz",
      "integrity": "sha512-LDJzPVEEEPR+y48z93A0Ed0yXb8pAByGWo/k5YYdYgpY2/2EsOsksJrq7lOHxryrVOn1ejG6oAp8ahvOIQD8sw==",
      "license": "MIT"
    },
    "node_modules/picocolors": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/picocolors/-/picocolors-1.1.1.tgz",
      "integrity": "sha512-xceH2snhtb5M9liqDsmEw56le376mTZkEX/jEb/RxNFyegNul7eNslCXP9FDj/Lcu0X8KEyMceP2ntpaHrDEVA==",
      "license": "ISC"
    },
    "node_modules/picomatch": {
      "version": "2.3.2",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-2.3.2.tgz",
      "integrity": "sha512-V7+vQEJ06Z+c5tSye8S+nHUfI51xoXIXjHQ99cQtKUkQqqO1kO/KCJUfZXuB47h/YBlDhah2H3hdUGXn8ie0oA==",
      "license": "MIT",
      "engines": {
        "node": ">=8.6"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/plist": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/plist/-/plist-3.1.1.tgz",
      "integrity": "sha512-ZIfcLJC+7E7FBFnDxm9MPmt7D+DidyQ26lewieO75AdhA2ayMtsJSES0iWzqJQbcVRSrTufQoy0DR94xHue0oA==",
      "license": "MIT",
      "dependencies": {
        "@xmldom/xmldom": "^0.9.10",
        "base64-js": "^1.5.1",
        "xmlbuilder": "^15.1.1"
      },
      "engines": {
        "node": ">=10.4.0"
      }
    },
    "node_modules/plist/node_modules/@xmldom/xmldom": {
      "version": "0.9.12",
      "resolved": "https://registry.npmjs.org/@xmldom/xmldom/-/xmldom-0.9.12.tgz",
      "integrity": "sha512-5AXjrcMClTryPe9LgZrygpB1lj7s0S9E0+W+AHaVKAVyHanafK86iPSvG5xHVSp/jC+VH1UXu0TAEmY279xH7A==",
      "license": "MIT",
      "engines": {
        "node": ">=14.6"
      }
    },
    "node_modules/pngjs": {
      "version": "3.4.0",
      "resolved": "https://registry.npmjs.org/pngjs/-/pngjs-3.4.0.tgz",
      "integrity": "sha512-NCrCHhWmnQklfH4MtJMRjZ2a8c80qXeMlQMv2uVp9ISJMTt562SbGd6n2oq0PaPgKm7Z6pL9E2UlLIhC+SHL3w==",
      "license": "MIT",
      "engines": {
        "node": ">=4.0.0"
      }
    },
    "node_modules/postcss": {
      "version": "8.5.33",
      "resolved": "https://registry.npmjs.org/postcss/-/postcss-8.5.33.tgz",
      "integrity": "sha512-RVHEU9/Pp1Fnjr/MpAJsZoADukCKhfIi15OunEYiGktIkYLkPVvC1sioWolGDS7XByMTx9m/IGbro0Js13zhnQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/postcss"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "nanoid": "^3.3.20",
        "picocolors": "^1.1.1",
        "source-map-js": "^1.2.2"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      }
    },
    "node_modules/pretty-format": {
      "version": "29.7.0",
      "resolved": "https://registry.npmjs.org/pretty-format/-/pretty-format-29.7.0.tgz",
      "integrity": "sha512-Pdlw/oPxN+aXdmM9R00JVC9WVFoCLTKJvDVLgmJ+qAffBMxsV85l/Lu7sNx4zSzPyoL2euImuEwHhOXdEgNFZQ==",
      "license": "MIT",
      "dependencies": {
        "@jest/schemas": "^29.6.3",
        "ansi-styles": "^5.0.0",
        "react-is": "^18.0.0"
      },
      "engines": {
        "node": "^14.15.0 || ^16.10.0 || >=18.0.0"
      }
    },
    "node_modules/pretty-format/node_modules/ansi-styles": {
      "version": "5.2.0",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-5.2.0.tgz",
      "integrity": "sha512-Cxwpt2SfTzTtXcfOlzGEee8O+c+MmUgGrNiBcXnuWxuFJHe6a5Hz7qwhwe5OgaSYI0IJvkLqWX1ASG+cJOkEiA==",
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-styles?sponsor=1"
      }
    },
    "node_modules/proc-log": {
      "version": "4.2.0",
      "resolved": "https://registry.npmjs.org/proc-log/-/proc-log-4.2.0.tgz",
      "integrity": "sha512-g8+OnU/L2v+wyiVK+D5fA34J7EH8jZ8DDlvwhRCMxmMj7UCBvxiO1mGeN+36JXIKF4zevU4kRBd8lVgG9vLelA==",
      "license": "ISC",
      "engines": {
        "node": "^14.17.0 || ^16.13.0 || >=18.0.0"
      }
    },
    "node_modules/progress": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/progress/-/progress-2.0.3.tgz",
      "integrity": "sha512-7PiHtLll5LdnKIMw100I+8xJXR5gW2QwWYkT6iJva0bXitZKa/XMrSbdmg3r2Xnaidz9Qumd0VPaMrZlF9V9sA==",
      "license": "MIT",
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/promise": {
      "version": "8.3.0",
      "resolved": "https://registry.npmjs.org/promise/-/promise-8.3.0.tgz",
      "integrity": "sha512-rZPNPKTOYVNEEKFaq1HqTgOwZD+4/YHS5ukLzQCypkj+OkYx7iv0mA91lJlpPPZ8vMau3IIGj5Qlwrx+8iiSmg==",
      "license": "MIT",
      "dependencies": {
        "asap": "~2.0.6"
      }
    },
    "node_modules/prompts": {
      "version": "2.4.2",
      "resolved": "https://registry.npmjs.org/prompts/-/prompts-2.4.2.tgz",
      "integrity": "sha512-NxNv/kLguCA7p3jE8oL2aEBsrJWgAakBpgmgK6lpPWV+WuOmY6r2/zbAVnP+T8bQlA0nzHXSJSJW0Hq7ylaD2Q==",
      "license": "MIT",
      "dependencies": {
        "kleur": "^3.0.3",
        "sisteransi": "^1.0.5"
      },
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/range-parser": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/range-parser/-/range-parser-1.2.1.tgz",
      "integrity": "sha512-Hrgsx+orqoygnmhFbKaHE6c296J+HTAQXoxEF6gNupROmmGJRoyzfG3ccAveqCBrwr/2yxQ5BVd/GTl5agOwSg==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/react": {
      "version": "19.3.0",
      "resolved": "https://registry.npmjs.org/react/-/react-19.3.0.tgz",
      "integrity": "sha512-E8LUcbtBWt20bbl2YoHfx4ZDBdxVTfOKtCZn9cDSJ4l6/nuoApcpIBcj47t2wZoVX8g2ZHuMHbiShgCR1T5Sog==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/react-devtools-core": {
      "version": "6.1.5",
      "resolved": "https://registry.npmjs.org/react-devtools-core/-/react-devtools-core-6.1.5.tgz",
      "integrity": "sha512-ePrwPfxAnB+7hgnEr8vpKxL9cmnp7F322t8oqcPshbIQQhDKgFDW4tjhF2wjVbdXF9O/nyuy3sQWd9JGpiLPvA==",
      "license": "MIT",
      "dependencies": {
        "shell-quote": "^1.6.1",
        "ws": "^7"
      }
    },
    "node_modules/react-is": {
      "version": "18.3.1",
      "resolved": "https://registry.npmjs.org/react-is/-/react-is-18.3.1.tgz",
      "integrity": "sha512-/LLMVyas0ljjAtoYiPqYiL8VWXzUUdThrmU5+n20DZv+a+ClRoevUzw5JxU+Ieh5/c87ytoTBV9G1FiKfNJdmg==",
      "license": "MIT"
    },
    "node_modules/react-native": {
      "version": "0.88.1",
      "resolved": "https://registry.npmjs.org/react-native/-/react-native-0.88.1.tgz",
      "integrity": "sha512-wajWcLZ93GCN7k4Uwh4CS4L2Ah8ohcvkOXnvIYmh4Yvuqho5j3APZ9qozK+nQrHWSgauq4h8D3HN5DKK84SrHA==",
      "license": "MIT",
      "dependencies": {
        "@react-native/asset-utils": "0.88.1",
        "@react-native/codegen": "0.88.1",
        "@react-native/community-cli-plugin": "0.88.1",
        "@react-native/gradle-plugin": "0.88.1",
        "@react-native/normalize-colors": "0.88.1",
        "@react-native/virtualized-lists": "0.88.1",
        "anser": "^1.4.9",
        "ansi-regex": "^5.0.0",
        "base64-js": "^1.5.1",
        "flow-enums-runtime": "^0.0.6",
        "flow-parser": "0.327.0",
        "hermes-compiler": "260318099.0.5",
        "invariant": "^2.2.4",
        "memoize-one": "^5.0.0",
        "metro-runtime": "^0.87.1",
        "metro-source-map": "^0.87.1",
        "nullthrows": "^1.1.1",
        "pretty-format": "^29.7.0",
        "promise": "^8.3.0",
        "react-devtools-core": "^6.1.5",
        "react-refresh": "^0.14.0",
        "regenerator-runtime": "^0.13.2",
        "scheduler": "0.28.0",
        "semver": "^7.1.3",
        "stacktrace-parser": "^0.1.10",
        "tinyglobby": "^0.2.15",
        "whatwg-fetch": "^3.0.0",
        "ws": "^7.5.10",
        "yargs": "^17.6.2"
      },
      "bin": {
        "react-native": "cli.js"
      },
      "engines": {
        "node": "^22.13.0 || ^24.3.0 || >= 26.0.0"
      },
      "peerDependencies": {
        "@types/react": "^19.1.1",
        "react": "^19.3.0"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/react-native-safe-area-context": {
      "version": "5.11.1",
      "resolved": "https://registry.npmjs.org/react-native-safe-area-context/-/react-native-safe-area-context-5.11.1.tgz",
      "integrity": "sha512-yCltXXwhwp42vMqfhAsH5BWgAysbLNgwfn3PDwNpOn/CgwfM+eMWgScZIbHbMzJYNLi5bKJEOIUEG4RwKNiECA==",
      "license": "MIT",
      "peerDependencies": {
        "react": "*",
        "react-native": "*"
      }
    },
    "node_modules/react-native/node_modules/flow-estree": {
      "version": "0.327.0",
      "resolved": "https://registry.npmjs.org/flow-estree/-/flow-estree-0.327.0.tgz",
      "integrity": "sha512-f9vK751YUzD0qaHSpKc5/qQM6gqOlgGS+4ZRqTNcZOpVqn3mC55yEQ6dUG2K1eaVm5FbKkz9CFWe6XNvrkQFQg==",
      "license": "MIT",
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/react-native/node_modules/flow-parser": {
      "version": "0.327.0",
      "resolved": "https://registry.npmjs.org/flow-parser/-/flow-parser-0.327.0.tgz",
      "integrity": "sha512-/MYZ5hXWf5ozpbdfUDmazMgQXviLxWEiRLH3MppEGDdW0itRVqmB5UaU7QX+SBCDNiq+gEesSVn8nlxmPDyDkw==",
      "license": "MIT",
      "dependencies": {
        "flow-estree": "0.327.0"
      },
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/react-refresh": {
      "version": "0.14.2",
      "resolved": "https://registry.npmjs.org/react-refresh/-/react-refresh-0.14.2.tgz",
      "integrity": "sha512-jCvmsr+1IUSMUyzOkRcvnVbX3ZYC6g9TDrDbFuFmRDq7PD4yaGbLKNQL6k2jnArV8hjYxh7hVhAZB6s9HDGpZA==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/regenerate": {
      "version": "1.5.0",
      "resolved": "https://registry.npmjs.org/regenerate/-/regenerate-1.5.0.tgz",
      "integrity": "sha512-1s+CxXjJ71i7LNVy8nYwg47XV4y6lAnOEhsMtSKq3WpmPfhl9LuKlTqKIn/3yUpE8lBz+W+TT88Bxyhnr0U4yw==",
      "license": "MIT"
    },
    "node_modules/regenerate-unicode-properties": {
      "version": "10.3.0",
      "resolved": "https://registry.npmjs.org/regenerate-unicode-properties/-/regenerate-unicode-properties-10.3.0.tgz",
      "integrity": "sha512-9ns8odR8e9q3otKeHj3DE80jZYKg6zVeZKE+zQmRKXFoVUcuiTGeO6iusDhPRoIQQPVPRvH+SfBhrTud4eczuw==",
      "license": "MIT",
      "dependencies": {
        "regenerate": "^1.4.2"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/regenerator-runtime": {
      "version": "0.13.11",
      "resolved": "https://registry.npmjs.org/regenerator-runtime/-/regenerator-runtime-0.13.11.tgz",
      "integrity": "sha512-kY1AZVr2Ra+t+piVaJ4gxaFaReZVH40AKNo7UCX6W+dEwBo/2oZJzqfuN1qLq1oL45o56cPaTXELwrTh8Fpggg==",
      "license": "MIT"
    },
    "node_modules/regexpu-core": {
      "version": "6.5.4",
      "resolved": "https://registry.npmjs.org/regexpu-core/-/regexpu-core-6.5.4.tgz",
      "integrity": "sha512-VpdamrZ9bw4YmvMZfTA3Yg8IHU9Guvg21bonvgjC4l3KfBkOqCPJesHakz7cQeE4Vh4zz4r4Gy6igAcnJxZv9g==",
      "license": "MIT",
      "dependencies": {
        "regenerate": "^1.5.0",
        "regenerate-unicode-properties": "^10.3.0",
        "regjsgen": "^0.8.0",
        "regjsparser": "^0.14.0",
        "unicode-match-property-ecmascript": "^2.0.0",
        "unicode-match-property-value-ecmascript": "^2.2.1"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/regjsgen": {
      "version": "0.8.0",
      "resolved": "https://registry.npmjs.org/regjsgen/-/regjsgen-0.8.0.tgz",
      "integrity": "sha512-RvwtGe3d7LvWiDQXeQw8p5asZUmfU1G/l6WbUXeHta7Y2PEIvBTwH6E2EfmYUK8pxcxEdEmaomqyp0vZZ7C+3Q==",
      "license": "MIT"
    },
    "node_modules/regjsparser": {
      "version": "0.14.1",
      "resolved": "https://registry.npmjs.org/regjsparser/-/regjsparser-0.14.1.tgz",
      "integrity": "sha512-IeYboCLG1KBNRksrZQIZ1SV5KVWZiR0ikFokOcA0n63vLvlaFvCsfxN+fd4aXwL0KW3YD+ByRzIgo9ZAHdbldw==",
      "license": "BSD-2-Clause",
      "dependencies": {
        "jsesc": "~3.1.0"
      },
      "bin": {
        "regjsparser": "bin/parser"
      }
    },
    "node_modules/require-directory": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/require-directory/-/require-directory-2.1.1.tgz",
      "integrity": "sha512-fGxEI7+wsG9xrvdjsrlmL22OMTTiHRwAMroiEeMgq8gzoLC/PQr7RsRDSTLUg/bZAZtF+TVIkHc6/4RIKrui+Q==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/resolve": {
      "version": "1.22.14",
      "resolved": "https://registry.npmjs.org/resolve/-/resolve-1.22.14.tgz",
      "integrity": "sha512-1ZjYvR9sbkiwC5+9QHetqW5HmA2pHRMaoupD01t2HlYnV/vydC2zPwLixhsMieSWVZt0JJRg5LVIk0Ow1D/TrA==",
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "is-core-module": "^2.18.0",
        "path-parse": "^1.0.7",
        "supports-preserve-symlinks-flag": "^1.0.0"
      },
      "bin": {
        "resolve": "bin/resolve"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/resolve-from": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/resolve-from/-/resolve-from-5.0.0.tgz",
      "integrity": "sha512-qYg9KP24dD5qka9J47d0aVky0N+b4fTU89LN9iDnjB5waksiC49rvMB0PrUJQGoTmH50XPiqOvAjDfaijGxYZw==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/resolve-workspace-root": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/resolve-workspace-root/-/resolve-workspace-root-2.0.1.tgz",
      "integrity": "sha512-nR23LHAvaI6aHtMg6RWoaHpdR4D881Nydkzi2CixINyg9T00KgaJdJI6Vwty+Ps8WLxZHuxsS0BseWjxSA4C+w==",
      "license": "MIT"
    },
    "node_modules/restore-cursor": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/restore-cursor/-/restore-cursor-2.0.0.tgz",
      "integrity": "sha512-6IzJLuGi4+R14vwagDHX+JrXmPVtPpn4mffDJ1UdR7/Edm87fl6yi8mMBIVvFtJaNTUvjughmW4hwLhRG7gC1Q==",
      "license": "MIT",
      "dependencies": {
        "onetime": "^2.0.0",
        "signal-exit": "^3.0.2"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/safe-buffer": {
      "version": "5.2.1",
      "resolved": "https://registry.npmjs.org/safe-buffer/-/safe-buffer-5.2.1.tgz",
      "integrity": "sha512-rp3So07KcdmmKbGvgaNxQSJr7bGVSVk5S9Eq1F+ppbRo70+YeaDxkw5Dd8NPN+GD6bjnYm2VuPuCXmpuYvmCXQ==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/feross"
        },
        {
          "type": "patreon",
          "url": "https://www.patreon.com/feross"
        },
        {
          "type": "consulting",
          "url": "https://feross.org/support"
        }
      ],
      "license": "MIT"
    },
    "node_modules/sandbox-cli-detector": {
      "version": "0.2.0",
      "resolved": "https://registry.npmjs.org/sandbox-cli-detector/-/sandbox-cli-detector-0.2.0.tgz",
      "integrity": "sha512-4lyHX0ZU0AZKwjgZ1InxZAa3PNpyEb8rOQ+Zss1ReYmhNzW0Q+h1zE5nvniXN0HaAWZaZE1zgVNEirb0R7LmNg==",
      "license": "MIT",
      "bin": {
        "sandbox-cli-detector": "dist/cli.js"
      },
      "engines": {
        "node": ">=18.18"
      }
    },
    "node_modules/sax": {
      "version": "1.6.1",
      "resolved": "https://registry.npmjs.org/sax/-/sax-1.6.1.tgz",
      "integrity": "sha512-42tBVwLWnaQvW5zc4HbZrTuWccECCZfBi92FDuwtqxasH+JbPB3/FOKb1m222K42R4WxuxzzMsTswfzgtSu64Q==",
      "license": "BlueOak-1.0.0",
      "engines": {
        "node": ">=11.0.0"
      }
    },
    "node_modules/scheduler": {
      "version": "0.28.0",
      "resolved": "https://registry.npmjs.org/scheduler/-/scheduler-0.28.0.tgz",
      "integrity": "sha512-juorfCmIkIw8tT+p5BXSm6PJjQF/ycEYmKyzURCIt/RaZIhL+PulbQ9Yu2z1HdOJDdqDTlxA1+xKBmHXJsczAw==",
      "license": "MIT"
    },
    "node_modules/semver": {
      "version": "7.8.6",
      "resolved": "https://registry.npmjs.org/semver/-/semver-7.8.6.tgz",
      "integrity": "sha512-9lpSSU4Mly3mrtruwLs1eLK6+gzbzqeBFwRNjIjE+9LuDpWdYctrQlQ3ej1Ilgi7gknpsTRnPoLP8DpCHqHIJw==",
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/send": {
      "version": "0.19.2",
      "resolved": "https://registry.npmjs.org/send/-/send-0.19.2.tgz",
      "integrity": "sha512-VMbMxbDeehAxpOtWJXlcUS5E8iXh6QmN+BkRX1GARS3wRaXEEgzCcB10gTQazO42tpNIya8xIyNx8fll1OFPrg==",
      "license": "MIT",
      "dependencies": {
        "debug": "2.6.9",
        "depd": "2.0.0",
        "destroy": "1.2.0",
        "encodeurl": "~2.0.0",
        "escape-html": "~1.0.3",
        "etag": "~1.8.1",
        "fresh": "~0.5.2",
        "http-errors": "~2.0.1",
        "mime": "1.6.0",
        "ms": "2.1.3",
        "on-finished": "~2.4.1",
        "range-parser": "~1.2.1",
        "statuses": "~2.0.2"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/send/node_modules/debug": {
      "version": "2.6.9",
      "resolved": "https://registry.npmjs.org/debug/-/debug-2.6.9.tgz",
      "integrity": "sha512-bC7ElrdJaJnPbAP+1EotYvqZsb3ecl5wi6Bfi6BJTUcNowp6cvspg0jXznRTKDjm/E7AdgFBVeAPVMNcKGsHMA==",
      "license": "MIT",
      "dependencies": {
        "ms": "2.0.0"
      }
    },
    "node_modules/send/node_modules/debug/node_modules/ms": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/ms/-/ms-2.0.0.tgz",
      "integrity": "sha512-Tpp60P6IUJDTuOq/5Z8cdskzJujfwqfOTkrwIwj7IRISpnkJnT6SyJ4PCPnGMoFjC9ddhal5KVIYtAt97ix05A==",
      "license": "MIT"
    },
    "node_modules/send/node_modules/encodeurl": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/encodeurl/-/encodeurl-2.0.3.tgz",
      "integrity": "sha512-mIteYONiEfc4xWf2F1WXovh1c8npzS00vNeiUPdwFF+QlVJni+gNvpQltLMQhob8rew/bWWc/bGTuUr0EUGt0w==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/express"
      }
    },
    "node_modules/send/node_modules/on-finished": {
      "version": "2.4.2",
      "resolved": "https://registry.npmjs.org/on-finished/-/on-finished-2.4.2.tgz",
      "integrity": "sha512-ATWUv387i+nLD49EiDoOft5scf32Vsdz3ktrQJG9bi7jRFmaXTssvyvj1EmeKVVgvesbqUtvQQvaS2TpTukAZQ==",
      "license": "MIT",
      "dependencies": {
        "ee-first": "1.1.1"
      },
      "engines": {
        "node": ">= 0.8"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/express"
      }
    },
    "node_modules/send/node_modules/statuses": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/statuses/-/statuses-2.0.2.tgz",
      "integrity": "sha512-DvEy55V3DB7uknRo+4iOGT5fP1slR8wQohVdknigZPMpMstaKJQWhwiYBACJE3Ul2pTnATihhBYnRhZQHGBiRw==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/serialize-error": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/serialize-error/-/serialize-error-2.1.0.tgz",
      "integrity": "sha512-ghgmKt5o4Tly5yEG/UJp8qTd0AN7Xalw4XBtDEKP655B699qMEtra1WlXeE6WIvdEG481JvRxULKsInq/iNysw==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/serve-static": {
      "version": "1.16.3",
      "resolved": "https://registry.npmjs.org/serve-static/-/serve-static-1.16.3.tgz",
      "integrity": "sha512-x0RTqQel6g5SY7Lg6ZreMmsOzncHFU7nhnRWkKgWuMTu5NN0DR5oruckMqRvacAN9d5w6ARnRBXl9xhDCgfMeA==",
      "license": "MIT",
      "dependencies": {
        "encodeurl": "~2.0.0",
        "escape-html": "~1.0.3",
        "parseurl": "~1.3.3",
        "send": "~0.19.1"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/serve-static/node_modules/encodeurl": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/encodeurl/-/encodeurl-2.0.3.tgz",
      "integrity": "sha512-mIteYONiEfc4xWf2F1WXovh1c8npzS00vNeiUPdwFF+QlVJni+gNvpQltLMQhob8rew/bWWc/bGTuUr0EUGt0w==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/express"
      }
    },
    "node_modules/setprototypeof": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/setprototypeof/-/setprototypeof-1.2.0.tgz",
      "integrity": "sha512-E5LDX7Wrp85Kil5bhZv46j8jOeboKq5JMmYM3gVGdGH8xFpPWXUMsNrlODCrkoxMEeNi/XZIwuRvY4XNwYMJpw==",
      "license": "ISC"
    },
    "node_modules/shebang-command": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/shebang-command/-/shebang-command-2.0.0.tgz",
      "integrity": "sha512-kHxr2zZpYtdmrN1qDjrrX/Z1rR1kG8Dx+gkpK1G4eXmvXswmcE1hTWBWYUzlraYw1/yZp6YuDY77YtvbN0dmDA==",
      "license": "MIT",
      "dependencies": {
        "shebang-regex": "^3.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/shebang-regex": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/shebang-regex/-/shebang-regex-3.0.0.tgz",
      "integrity": "sha512-7++dFhtcx3353uBaq8DDR4NuxBetBzC7ZQOhmTQInHEd6bSrXdiEyzCvG07Z44UYdLShWUyXt5M/yhz8ekcb1A==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/shell-quote": {
      "version": "1.12.0",
      "resolved": "https://registry.npmjs.org/shell-quote/-/shell-quote-1.12.0.tgz",
      "integrity": "sha512-PcByqNyT/38F2kDNi006HAMRJaULuBzq/FOsw3qdZvX/GA9W/jamDaRskgHjubHiftXK5sIFxLNkvrXUwcof6Q==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/signal-exit": {
      "version": "3.0.7",
      "resolved": "https://registry.npmjs.org/signal-exit/-/signal-exit-3.0.7.tgz",
      "integrity": "sha512-wnD2ZE+l+SPC/uoS0vXeE9L1+0wuaMqKlfz9AMUo38JsyLSBWSFcHR1Rri62LZc12vLr1gb3jl7iwQhgwpAbGQ==",
      "license": "ISC"
    },
    "node_modules/simple-plist": {
      "version": "1.3.1",
      "resolved": "https://registry.npmjs.org/simple-plist/-/simple-plist-1.3.1.tgz",
      "integrity": "sha512-iMSw5i0XseMnrhtIzRb7XpQEXepa9xhWxGUojHBL43SIpQuDQkh3Wpy67ZbDzZVr6EKxvwVChnVpdl8hEVLDiw==",
      "license": "MIT",
      "dependencies": {
        "bplist-creator": "0.1.0",
        "bplist-parser": "0.3.1",
        "plist": "^3.0.5"
      }
    },
    "node_modules/sisteransi": {
      "version": "1.0.5",
      "resolved": "https://registry.npmjs.org/sisteransi/-/sisteransi-1.0.5.tgz",
      "integrity": "sha512-bLGGlR1QxBcynn2d5YmDX4MGjlZvy2MRBDRNHLJ8VI6l6+9FUiyTFNJ0IveOSP0bcXgVDPRcfGqA0pjaqUpfVg==",
      "license": "MIT"
    },
    "node_modules/slugify": {
      "version": "1.6.9",
      "resolved": "https://registry.npmjs.org/slugify/-/slugify-1.6.9.tgz",
      "integrity": "sha512-vZ7rfeehZui7wQs438JXBckYLkIIdfHOXsaVEUMyS5fHo1483l1bMdo0EDSWYclY0yZKFOipDy4KHuKs6ssvdg==",
      "license": "MIT",
      "engines": {
        "node": ">=8.0.0"
      }
    },
    "node_modules/source-map": {
      "version": "0.5.7",
      "resolved": "https://registry.npmjs.org/source-map/-/source-map-0.5.7.tgz",
      "integrity": "sha512-LbrmJOMUSdEVxIKvdcJzQC+nQhe8FUZQTXQy6+I75skNgn3OoQ0DZA8YnFa7gp8tqtL3KPf1kmo0R5DoApeSGQ==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/source-map-js": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/source-map-js/-/source-map-js-1.2.4.tgz",
      "integrity": "sha512-J7ZjMvHd9O1fcT/5V09QWaaSl2BbWx3F6O08spde82Namf9UB0GxRVIPiNbVsdKkoizHiSpTodo3vp2bAy91MA==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/source-map-support": {
      "version": "0.5.21",
      "resolved": "https://registry.npmjs.org/source-map-support/-/source-map-support-0.5.21.tgz",
      "integrity": "sha512-uBHU3L3czsIyYXKX88fdrGovxdSCoTGDRZ6SYXtSRxLZUzHg5P/66Ht6uoUlHu9EZod+inXhKo3qQgwXUT/y1w==",
      "license": "MIT",
      "dependencies": {
        "buffer-from": "^1.0.0",
        "source-map": "^0.6.0"
      }
    },
    "node_modules/source-map-support/node_modules/source-map": {
      "version": "0.6.1",
      "resolved": "https://registry.npmjs.org/source-map/-/source-map-0.6.1.tgz",
      "integrity": "sha512-UjgapumWlbMhkBgzT7Ykc5YXUT46F0iKu8SGXq0bcwP5dz/h0Plj6enJqjz1Zbq2l5WaqYnrVbwWOWMyF3F47g==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/stackframe": {
      "version": "1.3.4",
      "resolved": "https://registry.npmjs.org/stackframe/-/stackframe-1.3.4.tgz",
      "integrity": "sha512-oeVtt7eWQS+Na6F//S4kJ2K2VbRlS9D43mAlMyVpVWovy9o+jfgH8O9agzANzaiLjclA0oYzUXEM4PurhSUChw==",
      "license": "MIT"
    },
    "node_modules/stacktrace-parser": {
      "version": "0.1.11",
      "resolved": "https://registry.npmjs.org/stacktrace-parser/-/stacktrace-parser-0.1.11.tgz",
      "integrity": "sha512-WjlahMgHmCJpqzU8bIBy4qtsZdU9lRlcZE3Lvyej6t4tuOuv1vk57OW3MBrj6hXBFx/nNoC9MPMTcr5YA7NQbg==",
      "license": "MIT",
      "dependencies": {
        "type-fest": "^0.7.1"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/statuses": {
      "version": "1.5.0",
      "resolved": "https://registry.npmjs.org/statuses/-/statuses-1.5.0.tgz",
      "integrity": "sha512-OpZ3zP+jT1PI7I8nemJX4AKmAX070ZkYPVWV/AaKTJl+tXCTGyVdC1a4SL8RUQYEwk/f34ZX8UTykN68FwrqAA==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/stream-buffers": {
      "version": "2.2.0",
      "resolved": "https://registry.npmjs.org/stream-buffers/-/stream-buffers-2.2.0.tgz",
      "integrity": "sha512-uyQK/mx5QjHun80FLJTfaWE7JtwfRMKBLkMne6udYOmvH0CawotVa7TfgYHzAnpphn4+TweIx1QKMnRIbipmUg==",
      "license": "Unlicense",
      "engines": {
        "node": ">= 0.10.0"
      }
    },
    "node_modules/string-width": {
      "version": "4.2.3",
      "resolved": "https://registry.npmjs.org/string-width/-/string-width-4.2.3.tgz",
      "integrity": "sha512-wKyQRQpjJ0sIp62ErSZdGsjMJWsap5oRNihHhu6G7JVO/9jIB6UyevL+tXuOqrng8j/cxKTWyWUwvSTriiZz/g==",
      "license": "MIT",
      "dependencies": {
        "emoji-regex": "^8.0.0",
        "is-fullwidth-code-point": "^3.0.0",
        "strip-ansi": "^6.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/strip-ansi": {
      "version": "6.0.1",
      "resolved": "https://registry.npmjs.org/strip-ansi/-/strip-ansi-6.0.1.tgz",
      "integrity": "sha512-Y38VPSHcqkFrCpFnQ9vuSXmquuv5oXOKpGeT6aGrr3o3Gc9AlVa6JBfUSOCnbxGGZF+/0ooI7KrPuUSztUdU5A==",
      "license": "MIT",
      "dependencies": {
        "ansi-regex": "^5.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/structured-headers": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/structured-headers/-/structured-headers-0.4.1.tgz",
      "integrity": "sha512-0MP/Cxx5SzeeZ10p/bZI0S6MpgD+yxAhi1BOQ34jgnMXsCq3j1t6tQnZu+KdlL7dvJTLT3g9xN8tl10TqgFMcg==",
      "license": "MIT"
    },
    "node_modules/supports-color": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/supports-color/-/supports-color-7.2.0.tgz",
      "integrity": "sha512-qpCAvRl9stuOHveKsn7HncJRvv501qIacKzQlO/+Lwxc9+0q2wLyv4Dfvt80/DPn2pqOBsJdDiogXGR9+OvwRw==",
      "license": "MIT",
      "dependencies": {
        "has-flag": "^4.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/supports-hyperlinks": {
      "version": "2.3.0",
      "resolved": "https://registry.npmjs.org/supports-hyperlinks/-/supports-hyperlinks-2.3.0.tgz",
      "integrity": "sha512-RpsAZlpWcDwOPQA22aCH4J0t7L8JmAvsCxfOSEwm7cQs3LshN36QaTkwd70DnBOXDWGssw2eUoc8CaRWT0XunA==",
      "license": "MIT",
      "dependencies": {
        "has-flag": "^4.0.0",
        "supports-color": "^7.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/supports-preserve-symlinks-flag": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/supports-preserve-symlinks-flag/-/supports-preserve-symlinks-flag-1.0.0.tgz",
      "integrity": "sha512-ot0WnXS9fgdkgIcePe6RHNk1WA8+muPa6cSjeR3V8K27q9BB1rTE3R1p7Hv0z1ZyAc8s6Vvv8DIyWf681MAt0w==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/terminal-link": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/terminal-link/-/terminal-link-2.1.1.tgz",
      "integrity": "sha512-un0FmiRUQNr5PJqy9kP7c40F5BOfpGlYTrxonDChEZB7pzZxRNp/bt+ymiy9/npwXya9KH99nJ/GXFIiUkYGFQ==",
      "license": "MIT",
      "dependencies": {
        "ansi-escapes": "^4.2.1",
        "supports-hyperlinks": "^2.0.0"
      },
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/terser": {
      "version": "5.51.4",
      "resolved": "https://registry.npmjs.org/terser/-/terser-5.51.4.tgz",
      "integrity": "sha512-VPi1CkDvCWLGUVIToctNBG+NdHbSXwOPjHJnQ3pdB0XknaldnI76wSkAFOGxV2ZdkzOP5d6gpQ5c58XvDghRvw==",
      "license": "BSD-2-Clause",
      "dependencies": {
        "@jridgewell/source-map": "^0.3.3",
        "acorn": "^8.15.0",
        "commander": "^2.20.0",
        "source-map-support": "~0.5.20"
      },
      "bin": {
        "terser": "bin/terser"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/terser/node_modules/commander": {
      "version": "2.20.3",
      "resolved": "https://registry.npmjs.org/commander/-/commander-2.20.3.tgz",
      "integrity": "sha512-GpVkmM8vF2vQUkj2LvZmD35JxeJOLCwJ9cUkugyk2nuhbv3+mJvpLYYt+0+USMxE+oj+ey/lJEnhZw75x/OMcQ==",
      "license": "MIT"
    },
    "node_modules/throat": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/throat/-/throat-5.0.0.tgz",
      "integrity": "sha512-fcwX4mndzpLQKBS1DVYhGAcYaYt7vsHNIvQV+WXMvnow5cgjPphq5CaayLaGsjRdSCKZFNGt7/GYAuXaNOiYCA==",
      "license": "MIT"
    },
    "node_modules/tinyglobby": {
      "version": "0.2.17",
      "resolved": "https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.17.tgz",
      "integrity": "sha512-wXR/dYpcqKmfWpEdZjiKJOwCNFndD0DMnrW/cYjVGttEkBfVgcLFHoNrlj47mjOVic9yyNu65alsgF4NQyTa2g==",
      "license": "MIT",
      "dependencies": {
        "fdir": "^6.5.0",
        "picomatch": "^4.0.4"
      },
      "engines": {
        "node": ">=12.0.0"
      },
      "funding": {
        "url": "https://github.com/sponsors/SuperchupuDev"
      }
    },
    "node_modules/tinyglobby/node_modules/fdir": {
      "version": "6.5.0",
      "resolved": "https://registry.npmjs.org/fdir/-/fdir-6.5.0.tgz",
      "integrity": "sha512-tIbYtZbucOs0BRGqPJkshJUYdL+SDH7dVM8gjy+ERp3WAUjLEFJE+02kanyHtwjWOnwrKYBiwAmM0p4kLJAnXg==",
      "license": "MIT",
      "engines": {
        "node": ">=12.0.0"
      },
      "peerDependencies": {
        "picomatch": "^3 || ^4"
      },
      "peerDependenciesMeta": {
        "picomatch": {
          "optional": true
        }
      }
    },
    "node_modules/tinyglobby/node_modules/picomatch": {
      "version": "4.0.7",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-4.0.7.tgz",
      "integrity": "sha512-qcJu88Q2IWqJsDD529JKMdwGm/dvInW4HvQnRwiH9JtihJvzGOscDtHE3x1pBKeUOTysQ8kVmLnJ2kJu7yhcGA==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/tmpl": {
      "version": "1.0.5",
      "resolved": "https://registry.npmjs.org/tmpl/-/tmpl-1.0.5.tgz",
      "integrity": "sha512-3f0uOEAQwIqGuWW2MVzYg8fV/QNnc/IpuJNG837rLuczAaLVHslWHZQj4IGiEl5Hs3kkbhwL9Ab7Hrsmuj+Smw==",
      "license": "BSD-3-Clause"
    },
    "node_modules/to-regex-range": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/to-regex-range/-/to-regex-range-5.0.1.tgz",
      "integrity": "sha512-65P7iz6X5yEr1cwcgvQxbbIw7Uk3gOy5dIdtZ4rDveLqhrdJP+Li/Hx6tyK0NEb+2GCyneCMJiGqrADCSNk8sQ==",
      "license": "MIT",
      "dependencies": {
        "is-number": "^7.0.0"
      },
      "engines": {
        "node": ">=8.0"
      }
    },
    "node_modules/toidentifier": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/toidentifier/-/toidentifier-1.0.1.tgz",
      "integrity": "sha512-o5sSPKEkg/DIQNmH43V0/uerLrpzVedkUh8tGNvaeXpfpuwjKenlSox/2O/BTlZUtEe+JG7s5YhEz608PlAHRA==",
      "license": "MIT",
      "engines": {
        "node": ">=0.6"
      }
    },
    "node_modules/toqr": {
      "version": "0.1.1",
      "resolved": "https://registry.npmjs.org/toqr/-/toqr-0.1.1.tgz",
      "integrity": "sha512-FWAPzCIHZHnrE/5/w9MPk0kK25hSQSH2IKhYh9PyjS3SG/+IEMvlwIHbhz+oF7xl54I+ueZlVnMjyzdSwLmAwA==",
      "license": "MIT"
    },
    "node_modules/type-fest": {
      "version": "0.7.1",
      "resolved": "https://registry.npmjs.org/type-fest/-/type-fest-0.7.1.tgz",
      "integrity": "sha512-Ne2YiiGN8bmrmJJEuTWTLJR32nh/JdL1+PSicowtNb0WFpn59GK8/lfD61bVtzguz7b3PBt74nxpv/Pw5po5Rg==",
      "license": "(MIT OR CC0-1.0)",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/typescript": {
      "version": "6.0.3",
      "resolved": "https://registry.npmjs.org/typescript/-/typescript-6.0.3.tgz",
      "integrity": "sha512-y2TvuxSZPDyQakkFRPZHKFm+KKVqIisdg9/CZwm9ftvKXLP8NRWj38/ODjNbr43SsoXqNuAisEf1GdCxqWcdBw==",
      "devOptional": true,
      "license": "Apache-2.0",
      "bin": {
        "tsc": "bin/tsc",
        "tsserver": "bin/tsserver"
      },
      "engines": {
        "node": ">=14.17"
      }
    },
    "node_modules/undici-types": {
      "version": "8.9.0",
      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-8.9.0.tgz",
      "integrity": "sha512-KTDyRTYX8sWmKXAikPHHSyc63CRPETMctyjKFupcC6OBLXT3xsN0e9aF7m+mIXutFWpUXuedtowG7iLOzp0kQg==",
      "license": "MIT"
    },
    "node_modules/unicode-canonical-property-names-ecmascript": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/unicode-canonical-property-names-ecmascript/-/unicode-canonical-property-names-ecmascript-2.0.1.tgz",
      "integrity": "sha512-dA8WbNeb2a6oQzAQ55YlT5vQAWGV9WXOsi3SskE3bcCdM0P4SDd+24zS/OCacdRq5BkdsRj9q3Pg6YyQoxIGqg==",
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/unicode-match-property-ecmascript": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/unicode-match-property-ecmascript/-/unicode-match-property-ecmascript-2.0.0.tgz",
      "integrity": "sha512-5kaZCrbp5mmbz5ulBkDkbY0SsPOjKqVS35VpL9ulMPfSl0J0Xsm+9Evphv9CoIZFwre7aJoa94AY6seMKGVN5Q==",
      "license": "MIT",
      "dependencies": {
        "unicode-canonical-property-names-ecmascript": "^2.0.0",
        "unicode-property-aliases-ecmascript": "^2.0.0"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/unicode-match-property-value-ecmascript": {
      "version": "2.2.1",
      "resolved": "https://registry.npmjs.org/unicode-match-property-value-ecmascript/-/unicode-match-property-value-ecmascript-2.2.1.tgz",
      "integrity": "sha512-JQ84qTuMg4nVkx8ga4A16a1epI9H6uTXAknqxkGF/aFfRLw1xC/Bp24HNLaZhHSkWd3+84t8iXnp1J0kYcZHhg==",
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/unicode-property-aliases-ecmascript": {
      "version": "2.2.0",
      "resolved": "https://registry.npmjs.org/unicode-property-aliases-ecmascript/-/unicode-property-aliases-ecmascript-2.2.0.tgz",
      "integrity": "sha512-hpbDzxUY9BFwX+UeBnxv3Sh1q7HFxj48DTmXchNgRa46lO8uj3/1iEn3MiNUYTg1g9ctIqXCCERn8gYZhHC5lQ==",
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/unpipe": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/unpipe/-/unpipe-1.0.0.tgz",
      "integrity": "sha512-pjy2bYhSsufwWlKwPc+l3cN7+wuJlK6uz0YdJEOlQDbl6jo/YlPi4mb8agUkVC8BF7V8NuzeyPNqRksA3hztKQ==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/update-browserslist-db": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/update-browserslist-db/-/update-browserslist-db-1.4.0.tgz",
      "integrity": "sha512-WPJuOnjI9FWDct4fB+ej4Mz8opLaw5CDcZ2t44tFZ0vIQVYWzBhWR3mkixuUj/A7+vY4V9+ApOZ2YYLwdgq46w==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "escalade": "^3.2.0",
        "picocolors": "^1.1.1"
      },
      "bin": {
        "update-browserslist-db": "cli.js"
      },
      "peerDependencies": {
        "browserslist": ">= 4.21.0"
      }
    },
    "node_modules/utils-merge": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/utils-merge/-/utils-merge-1.0.1.tgz",
      "integrity": "sha512-pMZTvIkT1d+TFGvDOqodOclx0QWkkgi6Tdoa8gC8ffGAAqz9pzPTZWAybbsHHoED/ztMtkv/VoYTYyShUn81hA==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4.0"
      }
    },
    "node_modules/validate-npm-package-name": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/validate-npm-package-name/-/validate-npm-package-name-5.0.1.tgz",
      "integrity": "sha512-OljLrQ9SQdOUqTaQxqL5dEfZWrXExyyWsozYlAWFawPVNuD83igl7uJD2RTkNMbniIYgt8l81eCJGIdQF7avLQ==",
      "license": "ISC",
      "engines": {
        "node": "^14.17.0 || ^16.13.0 || >=18.0.0"
      }
    },
    "node_modules/vary": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/vary/-/vary-1.1.2.tgz",
      "integrity": "sha512-BNGbWLfd0eUPabhkXUVm0j8uuvREyTh5ovRa/dyow/BqAbZJyC+5fU+IzQOzmAKzYqYRAISoRhdQr3eIZ/PXqg==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/vlq": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/vlq/-/vlq-1.0.1.tgz",
      "integrity": "sha512-gQpnTgkubC6hQgdIcRdYGDSDc+SaujOdyesZQMv6JlfQee/9Mp0Qhnys6WxDWvQnL5WZdT7o2Ul187aSt0Rq+w==",
      "license": "MIT"
    },
    "node_modules/walker": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/walker/-/walker-1.0.8.tgz",
      "integrity": "sha512-ts/8E8l5b7kY0vlWLewOkDXMmPdLcVV4GmOQLyxuSswIJsweeFZtAsMF7k1Nszz+TYBQrlYRmzOnr398y1JemQ==",
      "license": "Apache-2.0",
      "dependencies": {
        "makeerror": "1.0.12"
      }
    },
    "node_modules/wcwidth": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/wcwidth/-/wcwidth-1.0.1.tgz",
      "integrity": "sha512-XHPEwS0q6TaxcvG85+8EYkbiCux2XtWG2mkc47Ng2A77BQu9+DqIOJldST4HgPkuea7dvKSj5VgX3P1d4rW8Tg==",
      "license": "MIT",
      "dependencies": {
        "defaults": "^1.0.3"
      }
    },
    "node_modules/whatwg-fetch": {
      "version": "3.6.20",
      "resolved": "https://registry.npmjs.org/whatwg-fetch/-/whatwg-fetch-3.6.20.tgz",
      "integrity": "sha512-EqhiFU6daOA8kpjOWTL0olhVOF3i7OrFzSYiGsEMB8GcXS+RrzauAERX65xMeNWVqxA6HXH2m69Z9LaKKdisfg==",
      "license": "MIT"
    },
    "node_modules/whatwg-url-minimum": {
      "version": "0.2.0",
      "resolved": "https://registry.npmjs.org/whatwg-url-minimum/-/whatwg-url-minimum-0.2.0.tgz",
      "integrity": "sha512-BtjXU1caNcCFfETP2DhqSeVPfRDl2MTUitI107RE34rJXjR/izfUtR5IoTFOK1WqjNLXbbeqaCH/mQAOLjpc8g==",
      "license": "MIT"
    },
    "node_modules/which": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/which/-/which-2.0.2.tgz",
      "integrity": "sha512-BLI3Tl1TW3Pvl70l3yq3Y64i+awpwXqsGBYWkkqMtnbXgrMD+yj7rhW0kuEDxzJaYXGjEW5ogapKNMEKNMjibA==",
      "license": "ISC",
      "dependencies": {
        "isexe": "^2.0.0"
      },
      "bin": {
        "node-which": "bin/node-which"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/wrap-ansi": {
      "version": "7.0.0",
      "resolved": "https://registry.npmjs.org/wrap-ansi/-/wrap-ansi-7.0.0.tgz",
      "integrity": "sha512-YVGIj2kamLSTxw6NsZjoBxfSwsn0ycdesmc4p+Q21c5zPuZ1pl+NfxVdxPtdHvmNVOQ6XSYG4AUtyt/Fi7D16Q==",
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^4.0.0",
        "string-width": "^4.1.0",
        "strip-ansi": "^6.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/wrap-ansi?sponsor=1"
      }
    },
    "node_modules/ws": {
      "version": "7.5.14",
      "resolved": "https://registry.npmjs.org/ws/-/ws-7.5.14.tgz",
      "integrity": "sha512-u9Oi2nQ8SZnTUAf6spLLKF5TyqoG3Nbbrd4ai6Sjo4P24bycDewhQqtNMIg4bFpnpH/TD4qk4IuAVhT0HIIqug==",
      "license": "MIT",
      "engines": {
        "node": ">=8.3.0"
      },
      "peerDependencies": {
        "bufferutil": "^4.0.1",
        "utf-8-validate": "^5.0.2"
      },
      "peerDependenciesMeta": {
        "bufferutil": {
          "optional": true
        },
        "utf-8-validate": {
          "optional": true
        }
      }
    },
    "node_modules/xcode": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/xcode/-/xcode-4.0.0.tgz",
      "integrity": "sha512-dDaoWzc9EP2fp9FS9PVZUkyvFxY4y1TOV9pcKaKLk++Ei/qb97XDFEVP7GnW7Osii/TzVABJ0jq2F+9/lq0TVA==",
      "license": "Apache-2.0",
      "dependencies": {
        "simple-plist": "^1.3.1"
      },
      "engines": {
        "node": ">=14.17.0"
      }
    },
    "node_modules/xml2js": {
      "version": "0.6.0",
      "resolved": "https://registry.npmjs.org/xml2js/-/xml2js-0.6.0.tgz",
      "integrity": "sha512-eLTh0kA8uHceqesPqSE+VvO1CDDJWMwlQfB6LuN6T8w6MaDJ8Txm8P7s5cHD0miF0V+GGTZrDQfxPZQVsur33w==",
      "license": "MIT",
      "dependencies": {
        "sax": ">=0.6.0",
        "xmlbuilder": "~11.0.0"
      },
      "engines": {
        "node": ">=4.0.0"
      }
    },
    "node_modules/xml2js/node_modules/xmlbuilder": {
      "version": "11.0.1",
      "resolved": "https://registry.npmjs.org/xmlbuilder/-/xmlbuilder-11.0.1.tgz",
      "integrity": "sha512-fDlsI/kFEx7gLvbecc0/ohLG50fugQp8ryHzMTuW9vSa1GJ0XYWKnhsUx7oie3G98+r56aTQIUB4kht42R3JvA==",
      "license": "MIT",
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/xmlbuilder": {
      "version": "15.1.1",
      "resolved": "https://registry.npmjs.org/xmlbuilder/-/xmlbuilder-15.1.1.tgz",
      "integrity": "sha512-yMqGBqtXyeN1e3TGYvgNgDVZ3j84W4cwkOXQswghol6APgZWaff9lnbvN7MHYJOiXsvGPXtjTYJEiC9J2wv9Eg==",
      "license": "MIT",
      "engines": {
        "node": ">=8.0"
      }
    },
    "node_modules/y18n": {
      "version": "5.0.8",
      "resolved": "https://registry.npmjs.org/y18n/-/y18n-5.0.8.tgz",
      "integrity": "sha512-0pfFzegeDWJHJIAmTLRP2DwHjdF5s7jo9tuztdQxAhINCdvS+3nGINqPd00AphqJR/0LhANUS6/+7SCb98YOfA==",
      "license": "ISC",
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/yallist": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/yallist/-/yallist-3.1.1.tgz",
      "integrity": "sha512-a4UGQaWPH59mOXUYnAG2ewncQS4i4F43Tv3JoAM+s2VDAmS9NsK8GpDMLrCHPksFT7h3K6TOoUNn2pb7RoXx4g==",
      "license": "ISC"
    },
    "node_modules/yargs": {
      "version": "17.7.3",
      "resolved": "https://registry.npmjs.org/yargs/-/yargs-17.7.3.tgz",
      "integrity": "sha512-GZtjxm/J/4TSxuL3FNYjCmLktBTnIw/rVmKSIyKeYAZpmJB2ig9VauCC5xsa82GNKVKDAqpOn3KVzNt0zmrU0g==",
      "license": "MIT",
      "dependencies": {
        "cliui": "^8.0.1",
        "escalade": "^3.1.1",
        "get-caller-file": "^2.0.5",
        "require-directory": "^2.1.1",
        "string-width": "^4.2.3",
        "y18n": "^5.0.5",
        "yargs-parser": "^21.1.1"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/yargs-parser": {
      "version": "21.1.1",
      "resolved": "https://registry.npmjs.org/yargs-parser/-/yargs-parser-21.1.1.tgz",
      "integrity": "sha512-tVpsJW7DdjecAiFpbIB1e3qxIQsE6NoPc5/eTdrbbIC4h0LVsWhnoa3g+m2HclBIujHzsxZ4VJVA+GUuc2/LBw==",
      "license": "ISC",
      "engines": {
        "node": ">=12"
      }
    }
  }
}
'@
Write-RivalText 'mobile\package.json' @'
{
  "name": "rival-mobile",
  "version": "1.0.0",
  "main": "index.ts",
  "dependencies": {
    "expo": "~58.0.26",
    "expo-secure-store": "~58.0.3",
    "expo-status-bar": "~58.0.5",
    "react": "19.3.0",
    "react-native": "0.88.1",
    "react-native-safe-area-context": "~5.11.1"
  },
  "devDependencies": {
    "@types/node": "^26.6.6",
    "@types/react": "~19.3.0",
    "typescript": "~6.0.3"
  },
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "typecheck": "tsc --noEmit",
    "test": "node --experimental-strip-types --test tests/validation.test.ts tests/dateTime.test.ts"
  },
  "private": true
}
'@
Write-RivalText 'mobile\src\app\MatchFlow.tsx' @'
// Composición del Sprint 2: rivales, agentes libres, búsquedas de partido y ofertas.

import { useFreeAgentPanel } from '../controllers/useFreeAgentPanel';
import { useCreateMatchRequest, useOfferForm } from '../controllers/useMatchForms';
import { useMatchFeed, useMyMatchRequests, useOffers } from '../controllers/useMatches';
import type { Navigator } from '../controllers/useNavigator';
import { useFreeAgentSearch, useRivalSearch } from '../controllers/useScouting';
import type { MatchRequest } from '../domain/matchModels';
import type { Sport, TeamSummary, User } from '../domain/models';
import { CreateMatchRequestScreen } from '../ui/screens/CreateMatchRequestScreen';
import { FreeAgentPanelScreen } from '../ui/screens/FreeAgentPanelScreen';
import { FreeAgentSearchScreen } from '../ui/screens/FreeAgentSearchScreen';
import { MakeOfferScreen } from '../ui/screens/MakeOfferScreen';
import { MatchFeedScreen } from '../ui/screens/MatchFeedScreen';
import { MatchRequestsScreen } from '../ui/screens/MatchRequestsScreen';
import { OffersScreen } from '../ui/screens/OffersScreen';
import { RivalSearchScreen } from '../ui/screens/RivalSearchScreen';

export interface MatchCtx {
  user: User;
  token: string;
  navigator: Navigator;
  sports: Sport[];
}

export function Rivals({
  token,
  navigator,
  teamId,
  isAdmin,
}: MatchCtx & { teamId: number; isAdmin: boolean }) {
  return (
    <RivalSearchScreen
      controller={useRivalSearch(token, teamId)}
      canChallenge={isAdmin}
      onBack={navigator.goBack}
      onChallenge={(target) => navigator.push({ name: 'createMatchRequest', teamId, targetTeamId: target })}
    />
  );
}

export function FreeAgentPanel({ token, navigator, sports, user }: MatchCtx) {
  return (
    <FreeAgentPanelScreen
      controller={useFreeAgentPanel(token)}
      sports={sports}
      mySports={user.sports}
      onBack={navigator.goBack}
    />
  );
}

export function FreeAgentSearch({ token, navigator, team }: MatchCtx & { team: TeamSummary }) {
  return <FreeAgentSearchScreen controller={useFreeAgentSearch(token, team)} onBack={navigator.goBack} />;
}

export function Requests({
  token,
  navigator,
  teamId,
  isAdmin,
}: MatchCtx & { teamId: number; isAdmin: boolean }) {
  return (
    <MatchRequestsScreen
      controller={useMyMatchRequests(token, teamId)}
      isAdmin={isAdmin}
      onBack={navigator.goBack}
      onCreate={() => navigator.push({ name: 'createMatchRequest', teamId, targetTeamId: null })}
      onOpenOffers={(requestId, open) =>
        navigator.push({
          name: 'offers',
          requestId,
          isRequestAdmin: isAdmin,
          myTeamIds: [teamId],
          requestOpen: open,
        })
      }
    />
  );
}

export function CreateRequest({
  token,
  navigator,
  teamId,
  targetTeamId,
}: MatchCtx & { teamId: number; targetTeamId: number | null }) {
  const controller = useCreateMatchRequest(token, teamId, targetTeamId, () => {
    navigator.goBack();
    if (targetTeamId === null) return;
    navigator.push({ name: 'matchRequests', teamId, isAdmin: true });
  });
  return (
    <CreateMatchRequestScreen
      controller={controller}
      isChallenge={targetTeamId !== null}
      onBack={navigator.goBack}
    />
  );
}

export function Feed({ token, navigator, teamId, isAdmin }: MatchCtx & { teamId: number; isAdmin: boolean }) {
  return (
    <MatchFeedScreen
      controller={useMatchFeed(token, teamId)}
      isAdmin={isAdmin}
      onBack={navigator.goBack}
      onOffer={(request) => navigator.push({ name: 'makeOffer', teamId, request })}
      onMyOffers={(request) =>
        navigator.push({
          name: 'offers',
          requestId: request.id,
          isRequestAdmin: false,
          myTeamIds: [teamId],
          requestOpen: true,
        })
      }
    />
  );
}

export function Offer({
  token,
  navigator,
  teamId,
  request,
}: MatchCtx & { teamId: number; request: MatchRequest }) {
  const controller = useOfferForm(token, teamId, request, navigator.goBack);
  return <MakeOfferScreen controller={controller} request={request} onBack={navigator.goBack} />;
}

export function Offers(
  props: MatchCtx & { requestId: number; isRequestAdmin: boolean; myTeamIds: number[]; requestOpen: boolean },
) {
  return (
    <OffersScreen
      controller={useOffers(props.token, props.requestId)}
      isRequestAdmin={props.isRequestAdmin}
      myTeamIds={props.myTeamIds}
      requestOpen={props.requestOpen}
      onBack={props.navigator.goBack}
    />
  );
}
'@
Write-RivalText 'mobile\src\app\MatchRoutes.tsx' @'
// Elige la pantalla del Sprint 2 según la ruta actual.

import type { ReactNode } from 'react';

import type { Route } from '../controllers/useNavigator';
import type { MatchCtx } from './MatchFlow';
import {
  CreateRequest,
  Feed,
  FreeAgentPanel,
  FreeAgentSearch,
  Offer,
  Offers,
  Requests,
  Rivals,
} from './MatchFlow';

/** Devuelve la pantalla del Sprint 2 para la ruta, o null si la ruta no es de este flujo. */
export function renderMatchRoute(route: Route, ctx: MatchCtx): ReactNode | null {
  switch (route.name) {
    case 'rivals':
      return <Rivals {...ctx} teamId={route.teamId} isAdmin={route.isAdmin} />;
    case 'freeAgentPanel':
      return <FreeAgentPanel {...ctx} />;
    case 'freeAgentSearch':
      return <FreeAgentSearch {...ctx} team={route.team} />;
    case 'matchRequests':
      return <Requests {...ctx} teamId={route.teamId} isAdmin={route.isAdmin} />;
    case 'createMatchRequest':
      return <CreateRequest {...ctx} teamId={route.teamId} targetTeamId={route.targetTeamId} />;
    case 'matchFeed':
      return <Feed {...ctx} teamId={route.teamId} isAdmin={route.isAdmin} />;
    case 'makeOffer':
      return <Offer {...ctx} teamId={route.teamId} request={route.request} />;
    case 'offers':
      return (
        <Offers
          {...ctx}
          requestId={route.requestId}
          isRequestAdmin={route.isRequestAdmin}
          myTeamIds={route.myTeamIds}
          requestOpen={route.requestOpen}
        />
      );
    default:
      return null;
  }
}
'@
Write-RivalText 'mobile\src\app\SignedInFlow.tsx' @'
// Composición con sesión: inicio por rol, buscar y crear equipo, Mi equipo.

import { useCatalog } from '../controllers/useCatalog';
import { renderMatchRoute } from './MatchRoutes';
import { TeamActions } from './TeamActions';
import { useCreateTeamForm } from '../controllers/useCreateTeamForm';
import { useMyTeams } from '../controllers/useMyTeams';
import type { Navigator } from '../controllers/useNavigator';
import type { Session } from '../controllers/useSession';
import { useTeamDetail } from '../controllers/useTeamDetail';
import { useTeamSearch } from '../controllers/useTeamSearch';
import type { Sport, User } from '../domain/models';
import { Screen } from '../ui/components/Screen';
import { StateView } from '../ui/components/StateView';
import { CreateTeamScreen } from '../ui/screens/CreateTeamScreen';
import { HomeScreen } from '../ui/screens/HomeScreen';
import { TeamScreen } from '../ui/screens/TeamScreen';
import { TeamSearchScreen } from '../ui/screens/TeamSearchScreen';

interface Props {
  session: Session;
  user: User;
  token: string;
  navigator: Navigator;
}

interface Ctx extends Props {
  sports: Sport[];
}

function HomeContainer({ session, user, token, navigator }: Ctx) {
  const teams = useMyTeams(token);
  return (
    <HomeScreen
      user={user}
      myTeams={teams.state}
      onRefreshTeams={teams.handleRefresh}
      onSearchTeam={() => navigator.push({ name: 'teamSearch' })}
      onCreateTeam={() => navigator.push({ name: 'createTeam' })}
      onFreeAgent={() => navigator.push({ name: 'freeAgentPanel' })}
      onOpenTeam={(teamId) => navigator.push({ name: 'team', teamId })}
      onLogout={() => void session.handleLogout()}
    />
  );
}

function SearchContainer({ user, token, navigator, sports }: Ctx) {
  const controller = useTeamSearch(token, user.city);
  return (
    <TeamSearchScreen
      controller={controller}
      sports={sports}
      canJoinAsCoach={user.roles.includes('COACH')}
      onCreateTeam={() => navigator.push({ name: 'createTeam' })}
      onBack={navigator.goBack}
    />
  );
}

function CreateContainer({ user, token, navigator, sports }: Ctx) {
  const controller = useCreateTeamForm(token, user, (teamId) => {
    navigator.reset({ name: 'home' });
    navigator.push({ name: 'team', teamId });
  });
  return (
    <CreateTeamScreen
      controller={controller}
      sports={sports}
      isCoach={user.roles.includes('COACH')}
      onBack={navigator.goBack}
    />
  );
}

function TeamContainer({ user, token, navigator, teamId }: Ctx & { teamId: number }) {
  const controller = useTeamDetail(token, user.id, teamId, () => navigator.reset({ name: 'home' }));
  return (
    <TeamScreen
      controller={controller}
      userId={user.id}
      onBack={navigator.goBack}
      renderActions={(team, isAdmin) => <TeamActions team={team} isAdmin={isAdmin} navigator={navigator} />}
    />
  );
}

export function SignedInFlow(props: Props) {
  const catalog = useCatalog();
  const route = props.navigator.current;
  if (
    route.name === 'home' ||
    route.name === 'rolePicker' ||
    route.name === 'register' ||
    route.name === 'login'
  ) {
    return <HomeContainer {...props} sports={[]} />;
  }
  return (
    <StateView state={catalog.state} onRetry={catalog.handleRetry}>
      {(sports) => {
        if (route.name === 'teamSearch') return <SearchContainer {...props} sports={sports} />;
        if (route.name === 'createTeam') return <CreateContainer {...props} sports={sports} />;
        if (route.name === 'team') return <TeamContainer {...props} sports={sports} teamId={route.teamId} />;
        return renderMatchRoute(route, { ...props, sports });
      }}
    </StateView>
  );
}

export function LoadingScreen() {
  return (
    <Screen title="RIVAL">
      <StateView state={{ kind: 'loading' }}>{() => null}</StateView>
    </Screen>
  );
}
'@
Write-RivalText 'mobile\src\app\SignedOutFlow.tsx' @'
// Composición sin sesión: elegir rol → registro, o iniciar sesión.

import { useCatalog } from '../controllers/useCatalog';
import { useLoginForm } from '../controllers/useLoginForm';
import type { Navigator } from '../controllers/useNavigator';
import { useRegistrationForm } from '../controllers/useRegistrationForm';
import type { Session } from '../controllers/useSession';
import type { UserRole } from '../domain/models';
import { LoginScreen } from '../ui/screens/LoginScreen';
import { RegisterScreen } from '../ui/screens/RegisterScreen';
import { RolePickerScreen } from '../ui/screens/RolePickerScreen';

interface Props {
  session: Session;
  navigator: Navigator;
}

function RegisterContainer({
  role,
  session,
  onBack,
}: {
  role: UserRole;
  session: Session;
  onBack: () => void;
}) {
  const controller = useRegistrationForm(role, session.handleRegister);
  const catalog = useCatalog();
  return (
    <RegisterScreen
      controller={controller}
      catalog={catalog.state}
      onRetryCatalog={catalog.handleRetry}
      onBack={onBack}
    />
  );
}

function LoginContainer({ session, onBack }: { session: Session; onBack: () => void }) {
  return <LoginScreen controller={useLoginForm(session.handleLogin)} onBack={onBack} />;
}

export function SignedOutFlow({ session, navigator }: Props) {
  const route = navigator.current;
  if (route.name === 'register') {
    return <RegisterContainer role={route.role} session={session} onBack={navigator.goBack} />;
  }
  if (route.name === 'login') {
    return <LoginContainer session={session} onBack={navigator.goBack} />;
  }
  return (
    <RolePickerScreen
      onPickRole={(role) => navigator.push({ name: 'register', role })}
      onLogin={() => navigator.push({ name: 'login' })}
    />
  );
}
'@
Write-RivalText 'mobile\src\app\TeamActions.tsx' @'
// Acciones del equipo en "Mi equipo": buscar rival, búsquedas de partido, partidos para responder
// y agentes libres. Todos los miembros navegan; el backend decide quién puede actuar.

import type { Navigator } from '../controllers/useNavigator';
import type { TeamSummary } from '../domain/models';
import { PrimaryButton } from '../ui/components/PrimaryButton';

interface Props {
  team: TeamSummary;
  isAdmin: boolean;
  navigator: Navigator;
}

export function TeamActions({ team, isAdmin, navigator }: Props) {
  return (
    <>
      <PrimaryButton
        label="Buscar rival"
        onPress={() => navigator.push({ name: 'rivals', teamId: team.id, isAdmin })}
      />
      <PrimaryButton
        label="Partidos para mi equipo"
        variant="secondary"
        onPress={() => navigator.push({ name: 'matchFeed', teamId: team.id, isAdmin })}
      />
      <PrimaryButton
        label="Nuestras búsquedas de partido"
        variant="secondary"
        onPress={() => navigator.push({ name: 'matchRequests', teamId: team.id, isAdmin })}
      />
      {isAdmin ? (
        <PrimaryButton
          label="Buscar agentes libres"
          variant="secondary"
          onPress={() => navigator.push({ name: 'freeAgentSearch', team })}
        />
      ) : null}
    </>
  );
}
'@
Write-RivalText 'mobile\src\controllers\useAction.ts' @'
// Acción con cerrojo contra doble toque, estado ocupado y mensaje de resultado.

import { useCallback, useState } from 'react';

import { toAppError } from '../domain/appError';
import { useSubmitLock } from './useSubmitLock';

export interface Action {
  busy: boolean;
  message: string | null;
  run: (action: () => Promise<unknown>, success: string, after?: () => void) => Promise<void>;
}

export function useAction(): Action {
  const lock = useSubmitLock();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const run = useCallback(
    async (action: () => Promise<unknown>, success: string, after?: () => void) => {
      await lock(async () => {
        setBusy(true);
        setMessage(null);
        try {
          await action();
          setMessage(success);
          after?.();
        } catch (error) {
          setMessage(toAppError(error).message);
        } finally {
          setBusy(false);
        }
      });
    },
    [lock],
  );
  return { busy, message, run };
}
'@
Write-RivalText 'mobile\src\controllers\useCatalog.ts' @'
import { useCallback, useEffect, useState } from 'react';

import { errorToViewState } from '../domain/appError';
import type { Sport } from '../domain/models';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';
import { authApi } from '../services/authApi';

export function useCatalog(): { state: ViewState<Sport[]>; handleRetry: () => void } {
  const [state, setState] = useState<ViewState<Sport[]>>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    setState({ kind: 'loading' });
    authApi
      .sports()
      .then((sports) => {
        if (active) setState(successOrEmpty(sports, sports.length === 0, 'No hay deportes configurados.'));
      })
      .catch((error: unknown) => {
        if (active) setState(errorToViewState<Sport[]>(error));
      });
    return () => {
      active = false;
    };
  }, [attempt]);

  const handleRetry = useCallback(() => setAttempt((n) => n + 1), []);
  return { state, handleRetry };
}

export function sportName(sports: Sport[], code: string): string {
  return sports.find((s) => s.code === code)?.name ?? code;
}
'@
Write-RivalText 'mobile\src\controllers\useCreateTeamForm.ts' @'
import { useCallback, useState } from 'react';

import { toAppError } from '../domain/appError';
import type { User } from '../domain/models';
import type { FieldErrors } from '../domain/validation';
import { teamApi } from '../services/teamApi';
import { useSubmitLock } from './useSubmitLock';

export interface CreateTeamForm {
  name: string;
  sport: string | null;
  modality: string | null;
  city: string;
  neighborhood: string;
  asCoach: boolean;
}

type Field = keyof CreateTeamForm;

export interface CreateTeamController {
  form: CreateTeamForm;
  errors: FieldErrors<Field>;
  submitError: string | null;
  submitting: boolean;
  handleText: (field: 'name' | 'city' | 'neighborhood', value: string) => void;
  handleSport: (code: string) => void;
  handleModality: (code: string) => void;
  handleAsCoach: (value: boolean) => void;
  handleSubmit: () => Promise<void>;
}

function validate(form: CreateTeamForm): FieldErrors<Field> {
  const errors: FieldErrors<Field> = {};
  if (form.name.trim().length < 2) errors.name = 'Ponle un nombre al equipo (mínimo 2 letras).';
  if (!form.sport) errors.sport = 'Elige el deporte.';
  if (!form.modality) errors.modality = 'Elige la modalidad.';
  if (form.city.trim().length < 2) errors.city = 'Escribe la ciudad.';
  if (form.neighborhood.trim().length < 2) errors.neighborhood = 'Escribe el barrio donde juegan.';
  return errors;
}

export function useCreateTeamForm(
  token: string,
  user: User,
  onCreated: (teamId: number) => void,
): CreateTeamController {
  const [form, setForm] = useState<CreateTeamForm>({
    name: '',
    sport: user.sports[0] ?? null,
    modality: null,
    city: user.city,
    neighborhood: user.neighborhood,
    asCoach: user.roles.includes('COACH'),
  });
  const [errors, setErrors] = useState<FieldErrors<Field>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const lock = useSubmitLock();

  const handleText = useCallback((field: 'name' | 'city' | 'neighborhood', value: string) => {
    setForm((f) => ({ ...f, [field]: value }));
    setErrors((e) => ({ ...e, [field]: undefined }));
  }, []);

  const handleSubmit = useCallback(async () => {
    await lock(async () => {
      const found = validate(form);
      setErrors(found);
      if (Object.values(found).some(Boolean) || !form.sport || !form.modality) return;
      setSubmitting(true);
      setSubmitError(null);
      try {
        const created = await teamApi.create(token, {
          name: form.name.trim(),
          sport_code: form.sport,
          modality_code: form.modality,
          city: form.city.trim(),
          neighborhood: form.neighborhood.trim(),
          as_coach: form.asCoach,
        });
        onCreated(created.team.id);
      } catch (error) {
        setSubmitError(toAppError(error).message);
      } finally {
        setSubmitting(false);
      }
    });
  }, [form, lock, onCreated, token]);

  return {
    form,
    errors,
    submitError,
    submitting,
    handleText,
    handleSport: (code) => setForm((f) => ({ ...f, sport: code, modality: null })),
    handleModality: (code) => setForm((f) => ({ ...f, modality: code })),
    handleAsCoach: (value) => setForm((f) => ({ ...f, asCoach: value })),
    handleSubmit,
  };
}
'@
Write-RivalText 'mobile\src\controllers\useFreeAgentPanel.ts' @'
// Panel del jugador: aparecer como agente libre por deporte y responder invitaciones.

import { useCallback } from 'react';

import type { FreeAgentProfile, Invitation } from '../domain/matchModels';
import { scoutingApi } from '../services/scoutingApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface FreeAgentPanelController {
  profiles: Loader<FreeAgentProfile[]>;
  invitations: Loader<Invitation[]>;
  action: Action;
  handleToggle: (sportCode: string, active: boolean, current: FreeAgentProfile | undefined) => Promise<void>;
  handleRespond: (invitationId: number, accept: boolean) => Promise<void>;
}

export function useFreeAgentPanel(token: string): FreeAgentPanelController {
  const action = useAction();
  const profiles = useLoader(
    () => scoutingApi.myFreeAgent(token),
    () => false,
    '',
    `profiles|${token}`,
  );
  const invitations = useLoader(
    () => scoutingApi.myInvitations(token),
    (items) => items.length === 0,
    'No tienes invitaciones pendientes.',
    `invitations|${token}`,
  );
  const { handleReload: reloadProfiles } = profiles;
  const { handleReload: reloadInvitations } = invitations;

  const handleToggle = useCallback(
    (sportCode: string, active: boolean, current: FreeAgentProfile | undefined) =>
      action.run(
        () =>
          scoutingApi.setFreeAgent(token, {
            sport_code: sportCode,
            active,
            position: current?.position ?? null,
            note: current?.note ?? null,
          }),
        active ? 'Ahora apareces como agente libre.' : 'Ya no apareces como agente libre.',
        reloadProfiles,
      ),
    [action, reloadProfiles, token],
  );

  const handleRespond = useCallback(
    (invitationId: number, accept: boolean) =>
      action.run(
        () => scoutingApi.respondInvitation(token, invitationId, accept),
        accept ? '¡Bienvenido al equipo!' : 'Invitación rechazada.',
        () => {
          reloadInvitations();
          reloadProfiles();
        },
      ),
    [action, reloadInvitations, reloadProfiles, token],
  );

  return { profiles, invitations, action, handleToggle, handleRespond };
}
'@
Write-RivalText 'mobile\src\controllers\useLoader.ts' @'
// Carga genérica con los 7 estados: evita repetir el mismo efecto en cada controlador.

import { useCallback, useEffect, useRef, useState } from 'react';

import { errorToViewState } from '../domain/appError';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';

export interface Loader<T> {
  state: ViewState<T>;
  handleReload: () => void;
}

export function useLoader<T>(
  load: () => Promise<T>,
  isEmpty: (data: T) => boolean,
  emptyMessage: string,
  key: string,
): Loader<T> {
  const [state, setState] = useState<ViewState<T>>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);
  const loadRef = useRef(load);
  loadRef.current = load;

  useEffect(() => {
    let active = true;
    setState({ kind: 'loading' });
    loadRef
      .current()
      .then((data) => {
        if (active) setState(successOrEmpty(data, isEmpty(data), emptyMessage));
      })
      .catch((error: unknown) => {
        if (active) setState(errorToViewState<T>(error));
      });
    return () => {
      active = false;
    };
    // `key` resume todo lo que cambia la consulta; `isEmpty` y el mensaje son estables.
  }, [key, attempt]);

  return { state, handleReload: useCallback(() => setAttempt((n) => n + 1), []) };
}
'@
Write-RivalText 'mobile\src\controllers\useLoginForm.ts' @'
import { useCallback, useState } from 'react';

import { toAppError } from '../domain/appError';
import { useSubmitLock } from './useSubmitLock';

export interface LoginController {
  email: string;
  password: string;
  error: string | null;
  submitting: boolean;
  handleEmail: (value: string) => void;
  handlePassword: (value: string) => void;
  handleSubmit: () => Promise<void>;
}

export function useLoginForm(onLogin: (email: string, password: string) => Promise<void>): LoginController {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const lock = useSubmitLock();

  const handleSubmit = useCallback(async () => {
    await lock(async () => {
      if (!email.trim() || !password) {
        setError('Escribe tu correo y tu contraseña.');
        return;
      }
      setSubmitting(true);
      setError(null);
      try {
        await onLogin(email.trim(), password);
      } catch (caught) {
        setError(toAppError(caught).message);
      } finally {
        setSubmitting(false);
      }
    });
  }, [email, lock, onLogin, password]);

  return {
    email,
    password,
    error,
    submitting,
    handleEmail: setEmail,
    handlePassword: setPassword,
    handleSubmit,
  };
}
'@
Write-RivalText 'mobile\src\controllers\useMatchForms.ts' @'
// Formularios: publicar una búsqueda de partido (o retar) y hacer una oferta.

import { useCallback, useState } from 'react';

import { localTextInDays, isoToLocalText, parseLocalDateTime } from '../domain/dateTime';
import type { MatchRequest, PlaceKind, RefereeMode, SearchScope } from '../domain/matchModels';
import { matchApi } from '../services/matchApi';
import type { Action } from './useAction';
import { useAction } from './useAction';

export interface RequestForm {
  start: string;
  end: string;
  scope: SearchScope;
  radiusKm: number;
  referee: RefereeMode;
  place: PlaceKind;
  placeNote: string;
  message: string;
}

export interface FormController<F> {
  form: F;
  error: string | null;
  action: Action;
  handleChange: <K extends keyof F>(field: K, value: F[K]) => void;
  handleSubmit: () => Promise<void>;
}

function useForm<F>(initial: F) {
  const [form, setForm] = useState<F>(initial);
  const [error, setError] = useState<string | null>(null);
  const handleChange = useCallback(<K extends keyof F>(field: K, value: F[K]) => {
    setForm((f) => ({ ...f, [field]: value }));
    setError(null);
  }, []);
  return { form, error, setError, handleChange };
}

export function useCreateMatchRequest(
  token: string,
  teamId: number,
  targetTeamId: number | null,
  onDone: () => void,
): FormController<RequestForm> {
  const now = new Date();
  const { form, error, setError, handleChange } = useForm<RequestForm>({
    start: localTextInDays(now, 1, 8),
    end: localTextInDays(now, 3, 20),
    scope: targetTeamId ? 'CITY' : 'NEARBY',
    radiusKm: 5,
    referee: 'EITHER',
    place: 'TO_AGREE',
    placeNote: '',
    message: '',
  });
  const action = useAction();
  const handleSubmit = useCallback(async () => {
    const start = parseLocalDateTime(form.start);
    const end = parseLocalDateTime(form.end);
    if (!start || !end) {
      setError('Escribe las fechas como dd/mm/aaaa hh:mm, por ejemplo 28/11/2026 18:00.');
      return;
    }
    await action.run(
      () =>
        matchApi.create(token, teamId, {
          window_start: start,
          window_end: end,
          scope: form.scope,
          radius_km: form.scope === 'NEARBY' ? form.radiusKm : null,
          target_team_id: targetTeamId,
          referee_mode: form.referee,
          place_kind: form.place,
          place_note: form.placeNote.trim() || null,
          message: form.message.trim() || null,
        }),
      targetTeamId ? 'Reto enviado.' : 'Búsqueda publicada.',
      onDone,
    );
  }, [action, form, onDone, setError, targetTeamId, teamId, token]);
  return { form, error, action, handleChange, handleSubmit };
}

export interface OfferForm {
  start: string;
  referee: Exclude<RefereeMode, 'EITHER'>;
  place: PlaceKind;
  placeNote: string;
  message: string;
}

export function useOfferForm(
  token: string,
  teamId: number,
  request: MatchRequest,
  onDone: () => void,
): FormController<OfferForm> {
  const { form, error, setError, handleChange } = useForm<OfferForm>({
    // Nunca proponer por defecto una hora pasada: el inicio de la ventana o dentro de una hora.
    start: isoToLocalText(
      new Date(Math.max(Date.parse(request.window_start), Date.now() + 3_600_000)).toISOString(),
    ),
    referee: request.referee_mode === 'WITH' ? 'WITH' : 'WITHOUT',
    place: request.place_kind,
    placeNote: request.place_note ?? '',
    message: '',
  });
  const action = useAction();
  const handleSubmit = useCallback(async () => {
    const start = parseLocalDateTime(form.start);
    if (!start) {
      setError('Escribe la fecha como dd/mm/aaaa hh:mm.');
      return;
    }
    await action.run(
      () =>
        matchApi.offer(token, teamId, request.id, {
          proposed_start: start,
          referee_mode: form.referee,
          place_kind: form.place,
          place_note: form.placeNote.trim() || null,
          message: form.message.trim() || null,
        }),
      'Oferta enviada. Si envías otra, reemplaza a esta.',
      onDone,
    );
  }, [action, form, onDone, request.id, setError, teamId, token]);
  return { form, error, action, handleChange, handleSubmit };
}
'@
Write-RivalText 'mobile\src\controllers\useMatches.ts' @'
// Búsquedas de partido del equipo, partidos disponibles para responder y ofertas recibidas.

import { useCallback, useState } from 'react';

import type { MatchRequest, Offer, SearchScope } from '../domain/matchModels';
import { matchApi } from '../services/matchApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { Loader } from './useLoader';
import { useLoader } from './useLoader';

export interface MyRequestsController extends Loader<MatchRequest[]> {
  action: Action;
  handleCancel: (requestId: number) => Promise<void>;
}

export function useMyMatchRequests(token: string, teamId: number): MyRequestsController {
  const action = useAction();
  const loader = useLoader(
    () => matchApi.mine(token, teamId),
    (items) => items.length === 0,
    'Tu equipo aún no ha publicado búsquedas de partido.',
    `mine|${teamId}`,
  );
  const { handleReload } = loader;
  const handleCancel = useCallback(
    (requestId: number) =>
      action.run(() => matchApi.cancel(token, requestId), 'Búsqueda cancelada.', handleReload),
    [action, handleReload, token],
  );
  return { ...loader, action, handleCancel };
}

export interface FeedController extends Loader<MatchRequest[]> {
  scope: SearchScope;
  handleScope: (scope: SearchScope) => void;
}

export function useMatchFeed(token: string, teamId: number): FeedController {
  const [scope, setScope] = useState<SearchScope>('CITY');
  const loader = useLoader(
    () => matchApi.feed(token, teamId, scope, 5),
    (items) => items.length === 0,
    'No hay búsquedas de partido abiertas para tu equipo en este alcance.',
    `feed|${teamId}|${scope}`,
  );
  return { ...loader, scope, handleScope: setScope };
}

export interface OffersController extends Loader<Offer[]> {
  action: Action;
  handleDecide: (offerId: number, decision: 'accept' | 'reject' | 'withdraw') => Promise<void>;
}

const DECISION_MESSAGE = {
  accept: '¡Rival confirmado! Las demás ofertas quedaron reemplazadas.',
  reject: 'Oferta rechazada.',
  withdraw: 'Oferta retirada.',
} as const;

export function useOffers(token: string, requestId: number): OffersController {
  const action = useAction();
  const loader = useLoader(
    () => matchApi.offers(token, requestId),
    (items) => items.length === 0,
    'Todavía no hay ofertas. Los equipos cercanos verán tu búsqueda.',
    `offers|${requestId}`,
  );
  const { handleReload } = loader;
  const handleDecide = useCallback(
    (offerId: number, decision: 'accept' | 'reject' | 'withdraw') =>
      action.run(() => matchApi.decide(token, offerId, decision), DECISION_MESSAGE[decision], handleReload),
    [action, handleReload, token],
  );
  return { ...loader, action, handleDecide };
}
'@
Write-RivalText 'mobile\src\controllers\useMyTeams.ts' @'
import { useCallback, useEffect, useState } from 'react';

import { errorToViewState } from '../domain/appError';
import type { MyTeam } from '../domain/models';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';
import { teamApi } from '../services/teamApi';

export function useMyTeams(token: string): { state: ViewState<MyTeam[]>; handleRefresh: () => void } {
  const [state, setState] = useState<ViewState<MyTeam[]>>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    setState({ kind: 'loading' });
    teamApi
      .mine(token)
      .then((teams) => {
        if (active) {
          setState(successOrEmpty(teams, teams.length === 0, 'Todavía no tienes equipo.'));
        }
      })
      .catch((error: unknown) => {
        if (active) setState(errorToViewState<MyTeam[]>(error));
      });
    return () => {
      active = false;
    };
  }, [token, attempt]);

  const handleRefresh = useCallback(() => setAttempt((n) => n + 1), []);
  return { state, handleRefresh };
}
'@
Write-RivalText 'mobile\src\controllers\useNavigator.ts' @'
// Navegación simple por pila, sin dependencias nativas extra. El estado vive aquí, no en las vistas.

import { useCallback, useState } from 'react';

import type { MatchRequest } from '../domain/matchModels';
import type { TeamSummary, UserRole } from '../domain/models';

export type Route =
  | { name: 'rolePicker' }
  | { name: 'register'; role: UserRole }
  | { name: 'login' }
  | { name: 'home' }
  | { name: 'teamSearch' }
  | { name: 'createTeam' }
  | { name: 'team'; teamId: number }
  | { name: 'rivals'; teamId: number; isAdmin: boolean }
  | { name: 'freeAgentPanel' }
  | { name: 'freeAgentSearch'; team: TeamSummary }
  | { name: 'matchRequests'; teamId: number; isAdmin: boolean }
  | { name: 'createMatchRequest'; teamId: number; targetTeamId: number | null }
  | { name: 'matchFeed'; teamId: number; isAdmin: boolean }
  | { name: 'makeOffer'; teamId: number; request: MatchRequest }
  | { name: 'offers'; requestId: number; isRequestAdmin: boolean; myTeamIds: number[]; requestOpen: boolean };

export interface Navigator {
  current: Route;
  canGoBack: boolean;
  push: (route: Route) => void;
  goBack: () => void;
  reset: (route: Route) => void;
}

export function useNavigator(initial: Route): Navigator {
  const [stack, setStack] = useState<Route[]>([initial]);
  const push = useCallback((route: Route) => setStack((s) => [...s, route]), []);
  const goBack = useCallback(() => setStack((s) => (s.length > 1 ? s.slice(0, -1) : s)), []);
  const reset = useCallback((route: Route) => setStack([route]), []);
  return {
    current: stack[stack.length - 1] ?? initial,
    canGoBack: stack.length > 1,
    push,
    goBack,
    reset,
  };
}
'@
Write-RivalText 'mobile\src\controllers\usePagedLoader.ts' @'
// Carga paginada con "Cargar más": acumula páginas y se reinicia cuando cambia la consulta.

import { useCallback, useEffect, useState } from 'react';

import { toAppError } from '../domain/appError';
import type { ViewState } from '../domain/viewState';
import { useLoader } from './useLoader';
import { useSubmitLock } from './useSubmitLock';

export interface Page<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
}

export interface PagedLoader<T> {
  state: ViewState<Page<T>>;
  hasMore: boolean;
  loadingMore: boolean;
  moreError: string | null;
  handleReload: () => void;
  handleLoadMore: () => Promise<void>;
}

export function usePagedLoader<T>(
  load: (page: number) => Promise<Page<T>>,
  emptyMessage: string,
  key: string,
): PagedLoader<T> {
  const first = useLoader(
    () => load(1),
    (p) => p.items.length === 0,
    emptyMessage,
    key,
  );
  const [extra, setExtra] = useState<T[]>([]);
  const [lastPage, setLastPage] = useState(1);
  const [loadingMore, setLoadingMore] = useState(false);
  const [moreError, setMoreError] = useState<string | null>(null);
  const lock = useSubmitLock();

  useEffect(() => {
    setExtra([]);
    setLastPage(1);
    setMoreError(null);
  }, [key, first.state.kind]);

  const base = first.state.kind === 'success' ? first.state.data : null;
  const items = base ? [...base.items, ...extra] : [];
  const hasMore = base !== null && items.length < base.total;
  const state: ViewState<Page<T>> = base ? { kind: 'success', data: { ...base, items } } : first.state;

  const handleLoadMore = useCallback(async () => {
    if (!hasMore) return;
    await lock(async () => {
      setLoadingMore(true);
      setMoreError(null);
      try {
        const next = await load(lastPage + 1);
        setExtra((current) => [...current, ...next.items]);
        setLastPage(next.page);
      } catch (error) {
        setMoreError(toAppError(error).message);
      } finally {
        setLoadingMore(false);
      }
    });
  }, [hasMore, lastPage, load, lock]);

  return { state, hasMore, loadingMore, moreError, handleReload: first.handleReload, handleLoadMore };
}
'@
Write-RivalText 'mobile\src\controllers\useRegistrationForm.ts' @'
// Formulario de registro: conserva lo escrito si falla y muestra errores por campo.

import { useCallback, useState } from 'react';

import { toAppError } from '../domain/appError';
import type { RegisterPayload, UserRole } from '../domain/models';
import type { FieldErrors, RegistrationForm } from '../domain/validation';
import { parseBirthDate, validateRegistration } from '../domain/validation';
import { useSubmitLock } from './useSubmitLock';

type Field = keyof RegistrationForm;

export interface RegistrationController {
  form: RegistrationForm;
  errors: FieldErrors<Field>;
  submitError: string | null;
  submitting: boolean;
  handleChange: (field: Exclude<Field, 'sports' | 'role'>, value: string) => void;
  handleToggleSport: (code: string) => void;
  handleSubmit: () => Promise<void>;
}

export function useRegistrationForm(
  role: UserRole,
  onRegister: (payload: RegisterPayload) => Promise<void>,
): RegistrationController {
  const [form, setForm] = useState<RegistrationForm>({
    role,
    displayName: '',
    email: '',
    password: '',
    birthDate: '',
    sports: [],
    city: '',
    neighborhood: '',
    position: '',
  });
  const [errors, setErrors] = useState<FieldErrors<Field>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const lock = useSubmitLock();

  const handleChange = useCallback((field: Exclude<Field, 'sports' | 'role'>, value: string) => {
    setForm((f) => ({ ...f, [field]: value }));
    setErrors((e) => ({ ...e, [field]: undefined }));
  }, []);

  const handleToggleSport = useCallback((code: string) => {
    setForm((f) => ({
      ...f,
      sports: f.sports.includes(code) ? f.sports.filter((s) => s !== code) : [...f.sports, code],
    }));
    setErrors((e) => ({ ...e, sports: undefined }));
  }, []);

  const handleSubmit = useCallback(async () => {
    await lock(async () => {
      const found = validateRegistration(form, new Date());
      setErrors(found);
      if (Object.values(found).some(Boolean)) return;
      setSubmitting(true);
      setSubmitError(null);
      try {
        await onRegister({
          email: form.email.trim(),
          password: form.password,
          display_name: form.displayName.trim(),
          birth_date: parseBirthDate(form.birthDate) ?? '',
          role: form.role,
          sports: form.sports,
          city: form.city.trim(),
          neighborhood: form.neighborhood.trim(),
          position: form.position.trim() || null,
        });
      } catch (error) {
        setSubmitError(toAppError(error).message);
      } finally {
        setSubmitting(false);
      }
    });
  }, [form, lock, onRegister]);

  return { form, errors, submitError, submitting, handleChange, handleToggleSport, handleSubmit };
}
'@
Write-RivalText 'mobile\src\controllers\useScouting.ts' @'
// Buscar rivales y agentes libres, e invitar. Solo barrio, ciudad y rangos de distancia.

import { useCallback, useState } from 'react';

import type { FreeAgent, Rival, SearchScope } from '../domain/matchModels';
import type { TeamSummary } from '../domain/models';
import { scoutingApi } from '../services/scoutingApi';
import type { Action } from './useAction';
import { useAction } from './useAction';
import type { PagedLoader } from './usePagedLoader';
import { usePagedLoader } from './usePagedLoader';

export interface RivalSearchController extends PagedLoader<Rival> {
  scope: SearchScope;
  radiusKm: number;
  handleScope: (scope: SearchScope) => void;
  handleRadius: (km: number) => void;
}

export function useRivalSearch(token: string, teamId: number): RivalSearchController {
  const [scope, setScope] = useState<SearchScope>('NEARBY');
  const [radiusKm, setRadiusKm] = useState(5);
  const loader = usePagedLoader(
    (page) => scoutingApi.rivals(token, teamId, scope, radiusKm, page),
    'No hay equipos de tu deporte y modalidad en ese alcance. Prueba con "Mi ciudad".',
    `${teamId}|${scope}|${radiusKm}`,
  );
  return { ...loader, scope, radiusKm, handleScope: setScope, handleRadius: setRadiusKm };
}

export interface FreeAgentSearchController extends PagedLoader<FreeAgent> {
  onlyMyNeighborhood: boolean;
  invited: Record<number, string>;
  action: Action;
  handleOnlyNeighborhood: (value: boolean) => void;
  handleInvite: (userId: number) => Promise<void>;
}

export function useFreeAgentSearch(token: string, team: TeamSummary): FreeAgentSearchController {
  const [onlyMyNeighborhood, setOnlyMyNeighborhood] = useState(false);
  const [invited, setInvited] = useState<Record<number, string>>({});
  const action = useAction();
  const loader = usePagedLoader(
    (page) =>
      scoutingApi.freeAgents(
        token,
        team.sport_code,
        team.city,
        onlyMyNeighborhood ? team.neighborhood : undefined,
        page,
      ),
    'No hay agentes libres de este deporte por ahora.',
    `${team.id}|${onlyMyNeighborhood}`,
  );
  const handleInvite = useCallback(
    (userId: number) =>
      action.run(
        () => scoutingApi.invite(token, team.id, userId),
        'Invitación enviada. La persona debe aceptarla.',
        () => setInvited((s) => ({ ...s, [userId]: 'Invitado' })),
      ),
    [action, team.id, token],
  );
  return {
    ...loader,
    onlyMyNeighborhood,
    invited,
    action,
    handleOnlyNeighborhood: setOnlyMyNeighborhood,
    handleInvite,
  };
}
'@
Write-RivalText 'mobile\src\controllers\useSession.ts' @'
// Sesión: restaura el token guardado, registra, inicia y cierra sesión.

import { useCallback, useEffect, useState } from 'react';

import { toAppError } from '../domain/appError';
import type { RegisterPayload, SessionResponse, User } from '../domain/models';
import { authApi } from '../services/authApi';
import { setUnauthorizedHandler } from '../services/httpClient';
import { clearToken, readToken, saveToken } from '../services/tokenStore';

export type SessionStatus = 'restoring' | 'signedOut' | 'signedIn';

export interface Session {
  status: SessionStatus;
  user: User | null;
  token: string | null;
  handleRegister: (payload: RegisterPayload) => Promise<void>;
  handleLogin: (email: string, password: string) => Promise<void>;
  handleLogout: () => Promise<void>;
}

export function useSession(): Session {
  const [status, setStatus] = useState<SessionStatus>('restoring');
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const restore = async () => {
      try {
        const saved = await readToken();
        if (!saved) {
          if (active) setStatus('signedOut');
          return;
        }
        const me = await authApi.me(saved);
        if (!active) return;
        setUser(me);
        setToken(saved);
        setStatus('signedIn');
      } catch (error) {
        if (toAppError(error).status === 401) await clearToken().catch(() => undefined);
        if (active) setStatus('signedOut');
      }
    };
    void restore();
    return () => {
      active = false;
    };
  }, []);

  // Si el servidor rechaza el token a mitad de uso, se cierra la sesión en todo el app.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      void clearToken().catch(() => undefined);
      setToken(null);
      setUser(null);
      setStatus('signedOut');
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  const accept = useCallback(async (session: SessionResponse) => {
    // Si el almacenamiento seguro falla, la sesión sigue en memoria: la cuenta ya existe.
    await saveToken(session.token).catch(() => undefined);
    setToken(session.token);
    setUser(session.user);
    setStatus('signedIn');
  }, []);

  const handleRegister = useCallback(
    async (payload: RegisterPayload) => accept(await authApi.register(payload)),
    [accept],
  );

  const handleLogin = useCallback(
    async (email: string, password: string) => accept(await authApi.login(email, password)),
    [accept],
  );

  const handleLogout = useCallback(async () => {
    if (token) {
      await authApi.logout(token).catch(() => undefined);
    }
    await clearToken().catch(() => undefined);
    setToken(null);
    setUser(null);
    setStatus('signedOut');
  }, [token]);

  return { status, user, token, handleRegister, handleLogin, handleLogout };
}
'@
Write-RivalText 'mobile\src\controllers\useSubmitLock.ts' @'
// Cerrojo síncrono contra el doble toque: el estado de React llega un render tarde,
// una referencia no. Dos toques en el mismo instante ejecutan la acción una sola vez.

import { useCallback, useRef } from 'react';

export function useSubmitLock(): <T>(action: () => Promise<T>) => Promise<T | undefined> {
  const locked = useRef(false);
  return useCallback(async <T>(action: () => Promise<T>): Promise<T | undefined> => {
    if (locked.current) {
      return undefined;
    }
    locked.current = true;
    try {
      return await action();
    } finally {
      locked.current = false;
    }
  }, []);
}
'@
Write-RivalText 'mobile\src\controllers\useTeamDetail.ts' @'
// Mi equipo: plantilla, solicitudes pendientes (solo administrador), capitán y salir.

import { useCallback, useEffect, useState } from 'react';

import { errorToViewState, toAppError } from '../domain/appError';
import type { JoinRequest, TeamDetail } from '../domain/models';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';
import { teamApi } from '../services/teamApi';
import { useSubmitLock } from './useSubmitLock';

export interface TeamDetailController {
  detail: ViewState<TeamDetail>;
  requests: ViewState<JoinRequest[]>;
  isAdmin: boolean;
  busy: boolean;
  actionMessage: string | null;
  handleRefresh: () => void;
  handleDecide: (requestId: number, approve: boolean) => Promise<void>;
  handleSetCaptain: (userId: number) => Promise<void>;
  handleLeave: () => Promise<void>;
}

export function useTeamDetail(
  token: string,
  userId: number,
  teamId: number,
  onLeft: () => void,
): TeamDetailController {
  const [detail, setDetail] = useState<ViewState<TeamDetail>>({ kind: 'loading' });
  const [requests, setRequests] = useState<ViewState<JoinRequest[]>>({ kind: 'loading' });
  const [busy, setBusy] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const lock = useSubmitLock();

  const isAdmin = detail.kind === 'success' && detail.data.admin_user_id === userId;

  useEffect(() => {
    let active = true;
    setDetail({ kind: 'loading' });
    teamApi
      .detail(token, teamId)
      .then(async (data) => {
        if (!active) return;
        setDetail({ kind: 'success', data });
        if (data.admin_user_id !== userId) return;
        try {
          const pending = await teamApi.pendingRequests(token, teamId);
          if (active)
            setRequests(successOrEmpty(pending, pending.length === 0, 'No hay solicitudes pendientes.'));
        } catch (error) {
          if (active) setRequests(errorToViewState<JoinRequest[]>(error));
        }
      })
      .catch((error: unknown) => {
        if (active) setDetail(errorToViewState<TeamDetail>(error));
      });
    return () => {
      active = false;
    };
  }, [token, teamId, userId, attempt]);

  const run = useCallback(
    async (action: () => Promise<unknown>, success: string) => {
      await lock(async () => {
        setBusy(true);
        setActionMessage(null);
        try {
          await action();
          setActionMessage(success);
          setAttempt((n) => n + 1);
        } catch (error) {
          setActionMessage(toAppError(error).message);
        } finally {
          setBusy(false);
        }
      });
    },
    [lock],
  );

  return {
    detail,
    requests,
    isAdmin,
    busy,
    actionMessage,
    handleRefresh: useCallback(() => setAttempt((n) => n + 1), []),
    handleDecide: (requestId, approve) =>
      run(
        () => teamApi.decide(token, requestId, approve),
        approve ? 'Jugador aceptado.' : 'Solicitud rechazada.',
      ),
    handleSetCaptain: (memberId) =>
      run(() => teamApi.setCaptain(token, teamId, memberId), 'Capitán actualizado.'),
    handleLeave: () =>
      lock(async () => {
        setBusy(true);
        try {
          await teamApi.leave(token, teamId);
          onLeft();
        } catch (error) {
          setActionMessage(toAppError(error).message);
        } finally {
          setBusy(false);
        }
      }).then(() => undefined),
  };
}
'@
Write-RivalText 'mobile\src\controllers\useTeamSearch.ts' @'
// Buscar equipo por deporte, ciudad y nombre, con "Cargar más", y pedir unirse.
// Nunca hay ubicación exacta: solo ciudad y barrio.

import { useCallback, useEffect, useRef, useState } from 'react';

import { errorToViewState, toAppError } from '../domain/appError';
import type { TeamPage, TeamRole } from '../domain/models';
import type { ViewState } from '../domain/viewState';
import { successOrEmpty } from '../domain/viewState';
import { teamApi } from '../services/teamApi';

export type JoinStatus =
  | { kind: 'sending' }
  | { kind: 'sent'; message: string }
  | { kind: 'failed'; message: string };

export interface TeamSearchController {
  sport: string | null;
  city: string;
  text: string;
  state: ViewState<TeamPage>;
  hasMore: boolean;
  loadingMore: boolean;
  joinStatus: Record<number, JoinStatus>;
  handleSport: (code: string | null) => void;
  handleCity: (value: string) => void;
  handleText: (value: string) => void;
  handleSearch: () => void;
  handleLoadMore: () => Promise<void>;
  handleRequestJoin: (teamId: number, role: TeamRole) => Promise<void>;
}

const EMPTY_MESSAGE = 'No encontramos equipos con esos filtros. Prueba otra ciudad o crea el tuyo.';
const SENT_MESSAGE = 'Solicitud enviada. El DT o capitán debe aprobarla.';

export function useTeamSearch(token: string, defaultCity: string): TeamSearchController {
  const [sport, setSport] = useState<string | null>(null);
  const [city, setCity] = useState(defaultCity);
  const [text, setText] = useState('');
  const [state, setState] = useState<ViewState<TeamPage>>({ kind: 'loading' });
  const [loadingMore, setLoadingMore] = useState(false);
  const [joinStatus, setJoinStatus] = useState<Record<number, JoinStatus>>({});
  const [attempt, setAttempt] = useState(0);
  const joining = useRef(new Set<number>());

  const query = useCallback(
    (page: number) =>
      teamApi.search(token, {
        sport: sport ?? undefined,
        city: city.trim() || undefined,
        q: text.trim() || undefined,
        page,
      }),
    [token, sport, city, text],
  );

  useEffect(() => {
    let active = true;
    setState({ kind: 'loading' });
    query(1)
      .then((page) => {
        if (active) setState(successOrEmpty(page, page.items.length === 0, EMPTY_MESSAGE));
      })
      .catch((error: unknown) => {
        if (active) setState(errorToViewState<TeamPage>(error));
      });
    return () => {
      active = false;
    };
    // Ciudad y texto no disparan la búsqueda a propósito: se busca al pulsar Buscar
    // o al cambiar de deporte, no en cada letra (evita llamadas duplicadas).
  }, [token, sport, attempt]);

  const current = state.kind === 'success' ? state.data : null;
  const hasMore = current !== null && current.items.length < current.total;

  const handleLoadMore = useCallback(async () => {
    if (!current || loadingMore || !hasMore) return;
    setLoadingMore(true);
    try {
      const next = await query(current.page + 1);
      const known = new Set(current.items.map((t) => t.id));
      setState({
        kind: 'success',
        data: { ...next, items: [...current.items, ...next.items.filter((t) => !known.has(t.id))] },
      });
    } catch (error) {
      setState(errorToViewState<TeamPage>(error));
    } finally {
      setLoadingMore(false);
    }
  }, [current, hasMore, loadingMore, query]);

  const handleRequestJoin = useCallback(
    async (teamId: number, role: TeamRole) => {
      if (joining.current.has(teamId)) return;
      joining.current.add(teamId);
      setJoinStatus((s) => ({ ...s, [teamId]: { kind: 'sending' } }));
      try {
        await teamApi.requestJoin(token, teamId, role);
        setJoinStatus((s) => ({ ...s, [teamId]: { kind: 'sent', message: SENT_MESSAGE } }));
      } catch (error) {
        const appError = toAppError(error);
        // 409 "ya enviaste una solicitud" significa que la solicitud sí existe.
        const status: JoinStatus =
          appError.code === 'REQUEST_ALREADY_PENDING'
            ? { kind: 'sent', message: SENT_MESSAGE }
            : { kind: 'failed', message: appError.message };
        setJoinStatus((s) => ({ ...s, [teamId]: status }));
      } finally {
        joining.current.delete(teamId);
      }
    },
    [token],
  );

  return {
    sport,
    city,
    text,
    state,
    hasMore,
    loadingMore,
    joinStatus,
    handleSport: setSport,
    handleCity: setCity,
    handleText: setText,
    handleSearch: useCallback(() => setAttempt((n) => n + 1), []),
    handleLoadMore,
    handleRequestJoin,
  };
}
'@
Write-RivalText 'mobile\src\domain\appError.ts' @'
import type { ViewState } from './viewState';

export type AppErrorKind = 'network' | 'http';

export class AppError extends Error {
  readonly kind: AppErrorKind;
  readonly status: number;
  readonly code: string;
  readonly correlationId: string | null;
  readonly fields: string[];

  constructor(params: {
    kind: AppErrorKind;
    status: number;
    code: string;
    message: string;
    correlationId?: string | null;
    fields?: string[];
  }) {
    super(params.message);
    this.kind = params.kind;
    this.status = params.status;
    this.code = params.code;
    this.correlationId = params.correlationId ?? null;
    this.fields = params.fields ?? [];
  }
}

const OFFLINE_MESSAGE = 'Sin conexión. No se guardó nada; vuelve a intentarlo cuando tengas señal.';
const UNKNOWN_MESSAGE = 'Algo salió mal. Inténtalo de nuevo en un momento.';

export function toAppError(error: unknown): AppError {
  if (error instanceof AppError) {
    return error;
  }
  return new AppError({ kind: 'http', status: 0, code: 'UNKNOWN', message: UNKNOWN_MESSAGE });
}

export function errorToViewState<T>(error: unknown): ViewState<T> {
  const appError = toAppError(error);
  if (appError.kind === 'network') {
    return { kind: 'offline', message: OFFLINE_MESSAGE };
  }
  if (appError.status === 409) {
    return { kind: 'conflict', message: appError.message };
  }
  if (appError.status === 403) {
    return { kind: 'approvalGate', message: appError.message };
  }
  return { kind: 'error', message: appError.message, correlationId: appError.correlationId };
}

export function networkError(): AppError {
  return new AppError({ kind: 'network', status: 0, code: 'OFFLINE', message: OFFLINE_MESSAGE });
}
'@
Write-RivalText 'mobile\src\domain\dateTime.ts' @'
// Fechas y horas en hora de Colombia (UTC-5, sin horario de verano).
// Se escriben como dd/mm/aaaa hh:mm y viajan a la API en ISO 8601 con zona: ...-05:00.

const COLOMBIA_OFFSET_MINUTES = -5 * 60;
const PATTERN = /^(\d{2})\/(\d{2})\/(\d{4})\s+(\d{1,2}):(\d{2})$/;
const DAYS = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb'];

const pad = (n: number) => String(n).padStart(2, '0');

/** "28/11/2026 18:30" → "2026-11-28T18:30:00-05:00", o null si la fecha u hora no existen. */
export function parseLocalDateTime(text: string): string | null {
  const match = PATTERN.exec(text.trim());
  if (!match) return null;
  const [, dd, mm, yyyy, hh, min] = match;
  const day = Number(dd);
  const month = Number(mm);
  const year = Number(yyyy);
  const hour = Number(hh);
  const minute = Number(min);
  const probe = new Date(Date.UTC(year, month - 1, day));
  const validDate =
    probe.getUTCFullYear() === year && probe.getUTCMonth() === month - 1 && probe.getUTCDate() === day;
  if (!validDate || hour > 23 || minute > 59) return null;
  return `${yyyy}-${mm}-${dd}T${pad(hour)}:${min}:00-05:00`;
}

/** Fecha ISO (cualquier zona) → "sáb 28/11 18:30" en hora de Colombia. */
export function formatLocal(iso: string): string {
  const instant = Date.parse(iso);
  if (Number.isNaN(instant)) return iso;
  const local = new Date(instant + COLOMBIA_OFFSET_MINUTES * 60_000);
  const day = DAYS[local.getUTCDay()] ?? '';
  return `${day} ${pad(local.getUTCDate())}/${pad(local.getUTCMonth() + 1)} ${pad(local.getUTCHours())}:${pad(local.getUTCMinutes())}`;
}

/** Texto dd/mm/aaaa hh:mm para dentro de `days` días a la hora indicada (hora de Colombia). */
export function localTextInDays(now: Date, days: number, hour: number): string {
  const local = new Date(now.getTime() + COLOMBIA_OFFSET_MINUTES * 60_000 + days * 86_400_000);
  return `${pad(local.getUTCDate())}/${pad(local.getUTCMonth() + 1)}/${local.getUTCFullYear()} ${pad(hour)}:00`;
}

/** Fecha ISO → texto editable dd/mm/aaaa hh:mm en hora de Colombia. */
export function isoToLocalText(iso: string): string {
  const local = new Date(Date.parse(iso) + COLOMBIA_OFFSET_MINUTES * 60_000);
  return `${pad(local.getUTCDate())}/${pad(local.getUTCMonth() + 1)}/${local.getUTCFullYear()} ${pad(local.getUTCHours())}:${pad(local.getUTCMinutes())}`;
}
'@
Write-RivalText 'mobile\src\domain\labels.ts' @'
import type { TeamRole, UserRole } from './models';

export interface RoleOption {
  role: UserRole;
  title: string;
  description: string;
}

export const ROLE_OPTIONS: RoleOption[] = [
  { role: 'PLAYER', title: 'Jugador', description: 'Busca equipo o crea el tuyo y juega partidos.' },
  { role: 'COACH', title: 'Director técnico', description: 'Arma tu plantilla y administra tu equipo.' },
  { role: 'REFEREE', title: 'Árbitro', description: 'Únete a ligas y arbitra partidos cerca de ti.' },
  {
    role: 'VENUE_OWNER',
    title: 'Establecimiento deportivo',
    description: 'Publica tus canchas y horarios.',
  },
];

export const TEAM_ROLE_LABEL: Record<TeamRole, string> = {
  COACH: 'DT',
  CAPTAIN: 'Capitán',
  PLAYER: 'Jugador',
};

export function roleTitle(role: UserRole): string {
  return ROLE_OPTIONS.find((option) => option.role === role)?.title ?? role;
}
'@
Write-RivalText 'mobile\src\domain\matchLabels.ts' @'
import type { DistanceBand, MatchRequest, Offer, PlaceKind, RefereeMode, SearchScope } from './matchModels';

export const SCOPE_LABEL: Record<SearchScope, string> = {
  NEARBY: 'Cerca de mí',
  NEIGHBORHOOD: 'Mi barrio',
  CITY: 'Mi ciudad',
};

// Solo rangos: nunca la ubicación exacta de nadie.
export const DISTANCE_LABEL: Record<DistanceBand, string> = {
  UNDER_2_KM: 'a menos de 2 km',
  FROM_2_TO_5_KM: 'a 2–5 km',
  OVER_5_KM: 'a más de 5 km',
};

export const REFEREE_LABEL: Record<RefereeMode, string> = {
  WITH: 'Con árbitro',
  WITHOUT: 'Sin árbitro',
  EITHER: 'Con o sin árbitro',
};

export const PLACE_LABEL: Record<PlaceKind, string> = {
  VENUE: 'Cancha de establecimiento',
  INFORMAL: 'Lugar informal (parque, cancha de barrio)',
  TO_AGREE: 'Lugar por acordar',
};

export const REQUEST_STATUS_LABEL: Record<MatchRequest['status'], string> = {
  OPEN: 'Buscando rival',
  MATCHED: 'Rival encontrado',
  CANCELLED: 'Cancelada',
  EXPIRED: 'Venció',
};

export const OFFER_STATUS_LABEL: Record<Offer['status'], string> = {
  PENDING: 'Pendiente',
  ACCEPTED: 'Aceptada',
  REJECTED: 'Rechazada',
  WITHDRAWN: 'Retirada',
  SUPERSEDED: 'Reemplazada',
  CANCELLED: 'Cancelada',
};

export function distanceText(band: DistanceBand | null): string {
  return band ? DISTANCE_LABEL[band] : '';
}
'@
Write-RivalText 'mobile\src\domain\matchModels.ts' @'
// Contratos del Sprint 2: rivales, agentes libres, invitaciones, búsquedas de partido y ofertas.

import type { TeamSummary } from './models';

export type SearchScope = 'NEARBY' | 'NEIGHBORHOOD' | 'CITY';
export type DistanceBand = 'UNDER_2_KM' | 'FROM_2_TO_5_KM' | 'OVER_5_KM';
export type RefereeMode = 'WITH' | 'WITHOUT' | 'EITHER';
export type PlaceKind = 'VENUE' | 'INFORMAL' | 'TO_AGREE';

export interface Rival {
  team: TeamSummary;
  distance_band: DistanceBand | null;
}

export interface RivalPage {
  items: Rival[];
  page: number;
  page_size: number;
  total: number;
}

export interface FreeAgentProfile {
  sport_code: string;
  active: boolean;
  position: string | null;
  note: string | null;
}

export interface FreeAgent {
  user_id: number;
  display_name: string;
  sport_code: string;
  position: string | null;
  note: string | null;
  neighborhood: string;
  city: string;
}

export interface FreeAgentPage {
  items: FreeAgent[];
  page: number;
  page_size: number;
  total: number;
}

export interface Invitation {
  id: number;
  team: TeamSummary;
  message: string | null;
}

export interface MatchRequest {
  id: number;
  team: TeamSummary;
  target_team_id: number | null;
  scope: SearchScope;
  radius_km: number | null;
  window_start: string;
  window_end: string;
  referee_mode: RefereeMode;
  place_kind: PlaceKind;
  place_note: string | null;
  message: string | null;
  status: 'OPEN' | 'MATCHED' | 'CANCELLED' | 'EXPIRED';
  distance_band: DistanceBand | null;
  pending_offers: number;
  accepted_offer_id: number | null;
}

export interface Offer {
  id: number;
  request_id: number;
  team: TeamSummary;
  version: number;
  proposed_start: string;
  referee_mode: RefereeMode;
  place_kind: PlaceKind;
  place_note: string | null;
  message: string | null;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'WITHDRAWN' | 'SUPERSEDED' | 'CANCELLED';
}

export interface MatchRequestPayload {
  window_start: string;
  window_end: string;
  scope: SearchScope;
  radius_km: number | null;
  target_team_id: number | null;
  referee_mode: RefereeMode;
  place_kind: PlaceKind;
  place_note: string | null;
  message: string | null;
}

export interface OfferPayload {
  proposed_start: string;
  referee_mode: Exclude<RefereeMode, 'EITHER'>;
  place_kind: PlaceKind;
  place_note: string | null;
  message: string | null;
}
'@
Write-RivalText 'mobile\src\domain\models.ts' @'
// Contratos de datos con la API de RIVAL (backend/app/api/schemas_*.py).

export type UserRole = 'PLAYER' | 'COACH' | 'REFEREE' | 'VENUE_OWNER';
export type TeamRole = 'COACH' | 'CAPTAIN' | 'PLAYER';

export interface Modality {
  code: string;
  name: string;
  players_per_side: number;
}

export interface Sport {
  code: string;
  name: string;
  modalities: Modality[];
}

export interface User {
  id: number;
  email: string;
  display_name: string;
  roles: UserRole[];
  sports: string[];
  city: string;
  neighborhood: string;
  position: string | null;
}

export interface SessionResponse {
  token: string;
  user: User;
}

export interface RegisterPayload {
  email: string;
  password: string;
  display_name: string;
  birth_date: string;
  role: UserRole;
  sports: string[];
  city: string;
  neighborhood: string;
  position: string | null;
}

export interface TeamSummary {
  id: number;
  name: string;
  sport_code: string;
  modality_code: string;
  city: string;
  neighborhood: string;
  member_count: number;
  has_coach: boolean;
}

export interface Member {
  user_id: number;
  display_name: string;
  role: TeamRole;
  position: string | null;
}

export interface TeamDetail {
  team: TeamSummary;
  admin_user_id: number | null;
  members: Member[];
}

export interface MyTeam {
  team: TeamSummary;
  my_role: TeamRole;
  is_admin: boolean;
  pending_requests: number;
}

export interface TeamPage {
  items: TeamSummary[];
  page: number;
  page_size: number;
  total: number;
}

export interface JoinRequest {
  id: number;
  team_id: number;
  user_id: number;
  display_name: string;
  position: string | null;
  desired_role: TeamRole;
  message: string | null;
  status: string;
}

export interface CreateTeamPayload {
  name: string;
  sport_code: string;
  modality_code: string;
  city: string;
  neighborhood: string;
  as_coach: boolean;
}

export interface TeamSearchQuery {
  sport?: string;
  city?: string;
  q?: string;
  page?: number;
}
'@
Write-RivalText 'mobile\src\domain\validation.ts' @'
// Validaciones locales: ayudan a corregir antes de enviar. El backend vuelve a validar todo.

import type { UserRole } from './models';

export const MIN_AGE_YEARS = 18;
export const MIN_PASSWORD_LENGTH = 10;

export interface RegistrationForm {
  role: UserRole;
  displayName: string;
  email: string;
  password: string;
  birthDate: string; // dd/mm/aaaa tal como lo escribe la persona
  sports: string[];
  city: string;
  neighborhood: string;
  position: string;
}

export type FieldErrors<K extends string> = Partial<Record<K, string>>;

const DATE_PATTERN = /^(\d{2})\/(\d{2})\/(\d{4})$/;

/** Convierte dd/mm/aaaa a aaaa-mm-dd. Devuelve null si la fecha no existe. */
export function parseBirthDate(text: string): string | null {
  const match = DATE_PATTERN.exec(text.trim());
  if (!match) {
    return null;
  }
  const [, dd, mm, yyyy] = match;
  const day = Number(dd);
  const month = Number(mm);
  const year = Number(yyyy);
  const date = new Date(Date.UTC(year, month - 1, day));
  const valid =
    date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
  return valid ? `${yyyy}-${mm}-${dd}` : null;
}

/** Igual que el backend: un 29 de febrero cumple el 1 de marzo en años no bisiestos. */
export function isAdult(isoBirthDate: string, today: Date): boolean {
  const [year, month, day] = isoBirthDate.split('-').map(Number);
  if (year === undefined || month === undefined || day === undefined) {
    return false;
  }
  // Date.UTC desborda el 29/02 de un año no bisiesto al 01/03, que es la regla deseada.
  const comingOfAge = new Date(Date.UTC(year + MIN_AGE_YEARS, month - 1, day));
  const todayUtc = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  return todayUtc >= comingOfAge.getTime();
}

export function validateRegistration(
  form: RegistrationForm,
  today: Date,
): FieldErrors<keyof RegistrationForm> {
  const errors: FieldErrors<keyof RegistrationForm> = {};
  if (form.displayName.trim().length < 2) {
    errors.displayName = 'Escribe tu nombre (mínimo 2 letras).';
  }
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email.trim())) {
    errors.email = 'Escribe un correo válido, por ejemplo nombre@correo.com.';
  }
  if (form.password.length < MIN_PASSWORD_LENGTH) {
    errors.password = `Usa al menos ${MIN_PASSWORD_LENGTH} caracteres. Una frase funciona bien.`;
  }
  const iso = parseBirthDate(form.birthDate);
  if (iso === null) {
    errors.birthDate = 'Escribe tu fecha como dd/mm/aaaa, por ejemplo 05/10/1998.';
  } else if (!isAdult(iso, today)) {
    errors.birthDate = 'Por ahora RIVAL es solo para mayores de 18 años.';
  }
  if (form.sports.length === 0) {
    errors.sports = 'Elige al menos un deporte.';
  }
  if (form.city.trim().length < 2) {
    errors.city = 'Escribe tu ciudad.';
  }
  if (form.neighborhood.trim().length < 2) {
    errors.neighborhood = 'Escribe tu barrio. Solo se muestra el barrio, nunca tu ubicación exacta.';
  }
  return errors;
}
'@
Write-RivalText 'mobile\src\domain\viewState.ts' @'
// Los 7 estados obligatorios de toda vista que lee o cambia datos.

export type ViewState<T> =
  | { kind: 'loading' }
  | { kind: 'empty'; message: string }
  | { kind: 'error'; message: string; correlationId: string | null }
  | { kind: 'success'; data: T }
  | { kind: 'offline'; message: string }
  | { kind: 'conflict'; message: string }
  | { kind: 'approvalGate'; message: string };

export const loadingState = <T>(): ViewState<T> => ({ kind: 'loading' });

export const successOrEmpty = <T>(data: T, isEmpty: boolean, emptyMessage: string): ViewState<T> =>
  isEmpty ? { kind: 'empty', message: emptyMessage } : { kind: 'success', data };
'@
Write-RivalText 'mobile\src\services\authApi.ts' @'
import type { RegisterPayload, SessionResponse, Sport, User } from '../domain/models';
import { request } from './httpClient';

export const authApi = {
  register: (payload: RegisterPayload) =>
    request<SessionResponse>('POST', '/api/v1/auth/register', { body: payload }),

  login: (email: string, password: string) =>
    request<SessionResponse>('POST', '/api/v1/auth/login', { body: { email, password } }),

  logout: (token: string) => request<void>('POST', '/api/v1/auth/logout', { token }),

  me: (token: string) => request<User>('GET', '/api/v1/me', { token }),

  sports: async () => (await request<{ sports: Sport[] }>('GET', '/api/v1/catalog/sports')).sports,
};
'@
Write-RivalText 'mobile\src\services\config.ts' @'
// Dirección del backend. Se configura con EXPO_PUBLIC_API_URL (ver mobile/README.md).
// 10.0.2.2 es el computador anfitrión visto desde el emulador de Android.

const DEFAULT_API_URL = 'http://10.0.2.2:8000';

export const API_BASE_URL: string = (process.env.EXPO_PUBLIC_API_URL ?? DEFAULT_API_URL).replace(/\/+$/, '');

export const REQUEST_TIMEOUT_MS = 10_000;
'@
Write-RivalText 'mobile\src\services\httpClient.ts' @'
// Cliente HTTP único: tiempo límite, token de sesión y errores comprensibles.

import { AppError, networkError } from '../domain/appError';
import { API_BASE_URL, REQUEST_TIMEOUT_MS } from './config';

type Method = 'GET' | 'POST';

interface ErrorBody {
  code?: string;
  message?: string;
  correlation_id?: string;
  details?: string[];
}

let unauthorizedHandler: (() => void) | null = null;

/** La sesión registra aquí qué hacer si el servidor dice que el token ya no sirve. */
export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

function isErrorBody(value: unknown): value is ErrorBody {
  return typeof value === 'object' && value !== null && 'code' in value;
}

export async function request<T>(
  method: Method,
  path: string,
  options: { body?: unknown; token?: string | null; query?: Record<string, string | undefined> } = {},
): Promise<T> {
  const params = Object.entries(options.query ?? {})
    .filter((entry): entry is [string, string] => entry[1] !== undefined && entry[1] !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
  const url = `${API_BASE_URL}${path}${params ? `?${params}` : ''}`;
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response: Response;
  let data: unknown = null;
  try {
    response = await fetch(url, {
      method,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: controller.signal,
    });
    if (response.status !== 204) {
      data = await response.json().catch(() => null);
    }
  } catch {
    throw networkError();
  } finally {
    clearTimeout(timer);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  if (response.status === 401 && options.token) {
    unauthorizedHandler?.();
  }
  if (!response.ok) {
    const body = isErrorBody(data) ? data : {};
    throw new AppError({
      kind: 'http',
      status: response.status,
      code: body.code ?? 'HTTP_ERROR',
      message: body.message ?? 'No pudimos completar la acción. Inténtalo de nuevo.',
      correlationId: body.correlation_id ?? null,
      fields: body.details ?? [],
    });
  }
  return data as T;
}
'@
Write-RivalText 'mobile\src\services\matchApi.ts' @'
import type {
  MatchRequest,
  MatchRequestPayload,
  Offer,
  OfferPayload,
  SearchScope,
} from '../domain/matchModels';
import { request } from './httpClient';

type Status = { id: number; status: string };

export const matchApi = {
  create: (token: string, teamId: number, payload: MatchRequestPayload) =>
    request<MatchRequest>('POST', `/api/v1/teams/${teamId}/match-requests`, { token, body: payload }),

  mine: (token: string, teamId: number) =>
    request<MatchRequest[]>('GET', `/api/v1/teams/${teamId}/match-requests`, { token }),

  feed: (token: string, teamId: number, scope: SearchScope, radiusKm: number) =>
    request<MatchRequest[]>('GET', `/api/v1/teams/${teamId}/match-feed`, {
      token,
      query: { scope, radius_km: String(radiusKm) },
    }),

  cancel: (token: string, requestId: number) =>
    request<Status>('POST', `/api/v1/match-requests/${requestId}/cancel`, { token }),

  offer: (token: string, teamId: number, requestId: number, payload: OfferPayload) =>
    request<Status & { version: number }>(
      'POST',
      `/api/v1/teams/${teamId}/match-requests/${requestId}/offers`,
      {
        token,
        body: payload,
      },
    ),

  offers: (token: string, requestId: number) =>
    request<Offer[]>('GET', `/api/v1/match-requests/${requestId}/offers`, { token }),

  decide: (token: string, offerId: number, action: 'accept' | 'reject' | 'withdraw') =>
    request<Status>('POST', `/api/v1/offers/${offerId}/${action}`, { token }),
};
'@
Write-RivalText 'mobile\src\services\scoutingApi.ts' @'
import type {
  FreeAgentPage,
  FreeAgentProfile,
  Invitation,
  RivalPage,
  SearchScope,
} from '../domain/matchModels';
import { request } from './httpClient';

export const scoutingApi = {
  rivals: (token: string, teamId: number, scope: SearchScope, radiusKm: number, page: number) =>
    request<RivalPage>('GET', `/api/v1/teams/${teamId}/rivals`, {
      token,
      query: { scope, radius_km: String(radiusKm), page: String(page) },
    }),

  myFreeAgent: (token: string) => request<FreeAgentProfile[]>('GET', '/api/v1/me/free-agent', { token }),

  setFreeAgent: (token: string, profile: FreeAgentProfile) =>
    request<FreeAgentProfile>('POST', '/api/v1/me/free-agent', { token, body: profile }),

  freeAgents: (token: string, sport: string, city: string, neighborhood: string | undefined, page: number) =>
    request<FreeAgentPage>('GET', '/api/v1/free-agents', {
      token,
      query: { sport, city, neighborhood, page: String(page) },
    }),

  invite: (token: string, teamId: number, userId: number) =>
    request<{ id: number; status: string }>('POST', `/api/v1/teams/${teamId}/invitations`, {
      token,
      body: { user_id: userId },
    }),

  myInvitations: (token: string) => request<Invitation[]>('GET', '/api/v1/me/invitations', { token }),

  respondInvitation: (token: string, invitationId: number, accept: boolean) =>
    request<{ id: number; status: string }>(
      'POST',
      `/api/v1/invitations/${invitationId}/${accept ? 'accept' : 'reject'}`,
      { token },
    ),
};
'@
Write-RivalText 'mobile\src\services\teamApi.ts' @'
import type {
  CreateTeamPayload,
  JoinRequest,
  MyTeam,
  TeamDetail,
  TeamPage,
  TeamRole,
  TeamSearchQuery,
} from '../domain/models';
import { request } from './httpClient';

export const teamApi = {
  search: (token: string, query: TeamSearchQuery) =>
    request<TeamPage>('GET', '/api/v1/teams', {
      token,
      query: { sport: query.sport, city: query.city, q: query.q, page: query.page?.toString() },
    }),

  create: (token: string, payload: CreateTeamPayload) =>
    request<TeamDetail>('POST', '/api/v1/teams', { token, body: payload }),

  detail: (token: string, teamId: number) => request<TeamDetail>('GET', `/api/v1/teams/${teamId}`, { token }),

  mine: (token: string) => request<MyTeam[]>('GET', '/api/v1/me/teams', { token }),

  requestJoin: (token: string, teamId: number, desiredRole: TeamRole) =>
    request<{ id: number; status: string }>('POST', `/api/v1/teams/${teamId}/join-requests`, {
      token,
      body: { desired_role: desiredRole },
    }),

  pendingRequests: (token: string, teamId: number) =>
    request<JoinRequest[]>('GET', `/api/v1/teams/${teamId}/join-requests`, { token }),

  decide: (token: string, requestId: number, approve: boolean) =>
    request<{ id: number; status: string }>(
      'POST',
      `/api/v1/join-requests/${requestId}/${approve ? 'approve' : 'reject'}`,
      { token },
    ),

  setCaptain: (token: string, teamId: number, userId: number) =>
    request<TeamDetail>('POST', `/api/v1/teams/${teamId}/captain`, {
      token,
      body: { user_id: userId },
    }),

  leave: (token: string, teamId: number) => request<void>('POST', `/api/v1/teams/${teamId}/leave`, { token }),
};
'@
Write-RivalText 'mobile\src\services\tokenStore.ts' @'
// El token se guarda en el almacenamiento seguro del sistema (Keychain / Keystore).

import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'rival.session.token';

export async function readToken(): Promise<string | null> {
  return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function saveToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function clearToken(): Promise<void> {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}
'@
Write-RivalText 'mobile\src\ui\components\Card.tsx' @'
import type { ReactNode } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, font, radius, space } from '../theme';

interface Props {
  title: string;
  subtitle?: string;
  badge?: string;
  onPress?: () => void;
  children?: ReactNode;
}

export function Card({ title, subtitle, badge, onPress, children }: Props) {
  const body = (
    <>
      <View style={styles.headerRow}>
        <Text style={styles.title}>{title}</Text>
        {badge ? <Text style={styles.badge}>{badge}</Text> : null}
      </View>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      {children}
    </>
  );
  if (!onPress) {
    return <View style={styles.card}>{body}</View>;
  }
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={subtitle ? `${title}. ${subtitle}` : title}
      style={({ pressed }) => [styles.card, pressed && styles.pressed]}
    >
      {body}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    gap: space.sm,
    padding: space.md,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  pressed: { opacity: 0.85 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', gap: space.sm },
  title: { flex: 1, color: colors.text, fontSize: font.heading, fontWeight: '600' },
  subtitle: { color: colors.textMuted, fontSize: font.small },
  badge: {
    color: colors.accent,
    fontSize: font.small,
    fontWeight: '700',
    borderWidth: 1,
    borderColor: colors.accent,
    borderRadius: radius.sm,
    paddingHorizontal: space.sm,
  },
});
'@
Write-RivalText 'mobile\src\ui\components\ChoiceChips.tsx' @'
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, font, MIN_TOUCH, radius, space } from '../theme';

export interface Choice {
  value: string;
  label: string;
}

interface Props {
  label: string;
  choices: Choice[];
  selected: string[];
  onToggle: (value: string) => void;
  error?: string;
}

// Selección con fichas: el estado elegido se marca con borde, peso y "✓", no solo con color.
export function ChoiceChips({ label, choices, selected, onToggle, error }: Props) {
  return (
    <View style={styles.wrapper} accessibilityRole="radiogroup" accessibilityLabel={label}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.row}>
        {choices.map((choice) => {
          const isOn = selected.includes(choice.value);
          return (
            <Pressable
              key={choice.value}
              onPress={() => onToggle(choice.value)}
              accessibilityRole="checkbox"
              accessibilityState={{ checked: isOn }}
              accessibilityLabel={choice.label}
              style={[styles.chip, isOn && styles.chipOn]}
            >
              <Text style={[styles.chipText, isOn && styles.chipTextOn]}>
                {isOn ? `✓ ${choice.label}` : choice.label}
              </Text>
            </Pressable>
          );
        })}
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: space.xs },
  label: { color: colors.text, fontSize: font.small, fontWeight: '600' },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: space.sm },
  chip: {
    minHeight: MIN_TOUCH,
    justifyContent: 'center',
    paddingHorizontal: space.md,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  chipOn: { borderColor: colors.accent, borderWidth: 2 },
  chipText: { color: colors.text, fontSize: font.small },
  chipTextOn: { color: colors.accent, fontWeight: '700' },
  error: { color: colors.danger, fontSize: font.small },
});
'@
Write-RivalText 'mobile\src\ui\components\LoadMore.tsx' @'
import { StyleSheet, Text } from 'react-native';

import { colors, font } from '../theme';
import { PrimaryButton } from './PrimaryButton';

interface Props {
  hasMore: boolean;
  loading: boolean;
  error: string | null;
  onPress: () => void;
}

export function LoadMore({ hasMore, loading, error, onPress }: Props) {
  return (
    <>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {hasMore ? (
        <PrimaryButton label="Cargar más" variant="secondary" loading={loading} onPress={onPress} />
      ) : null}
    </>
  );
}

const styles = StyleSheet.create({
  error: { color: colors.danger, fontSize: font.small },
});
'@
Write-RivalText 'mobile\src\ui\components\PrimaryButton.tsx' @'
import { ActivityIndicator, Pressable, StyleSheet, Text } from 'react-native';

import { colors, font, MIN_TOUCH, radius, space } from '../theme';

interface Props {
  label: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
}

export function PrimaryButton({
  label,
  onPress,
  loading = false,
  disabled = false,
  variant = 'primary',
}: Props) {
  const inactive = disabled || loading;
  return (
    <Pressable
      onPress={onPress}
      disabled={inactive}
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityState={{ disabled: inactive, busy: loading }}
      style={({ pressed }) => [
        styles.base,
        variant === 'primary' && styles.primary,
        variant === 'secondary' && styles.secondary,
        variant === 'danger' && styles.danger,
        inactive && styles.inactive,
        pressed && !inactive && styles.pressed,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'secondary' ? colors.accent : colors.accentText} />
      ) : (
        <Text style={[styles.label, variant === 'secondary' && styles.secondaryLabel]}>{label}</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: MIN_TOUCH,
    borderRadius: radius.sm,
    paddingHorizontal: space.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primary: { backgroundColor: colors.accent },
  secondary: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.accent },
  danger: { backgroundColor: colors.danger },
  inactive: { backgroundColor: colors.disabled, borderColor: colors.disabled },
  pressed: { opacity: 0.85 },
  label: { color: colors.accentText, fontSize: font.body, fontWeight: '600' },
  secondaryLabel: { color: colors.accent },
});
'@
Write-RivalText 'mobile\src\ui\components\Screen.tsx' @'
import type { ReactNode } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { colors, font, MIN_TOUCH, space } from '../theme';

interface Props {
  title: string;
  onBack?: () => void;
  children: ReactNode;
}

export function Screen({ title, onBack, children }: Props) {
  const insets = useSafeAreaInsets();
  return (
    <View style={[styles.root, { paddingTop: insets.top, paddingBottom: insets.bottom }]}>
      <View style={styles.header}>
        {onBack ? (
          <Pressable
            onPress={onBack}
            accessibilityRole="button"
            accessibilityLabel="Volver"
            style={styles.back}
          >
            <Text style={styles.backText}>‹ Volver</Text>
          </Pressable>
        ) : null}
        <Text style={styles.title} accessibilityRole="header">
          {title}
        </Text>
      </View>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        {children}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  header: { paddingHorizontal: space.md, paddingTop: space.sm, paddingBottom: space.sm },
  back: { minHeight: MIN_TOUCH, justifyContent: 'center', alignSelf: 'flex-start' },
  backText: { color: colors.accent, fontSize: font.body },
  title: { color: colors.text, fontSize: font.title, fontWeight: '700' },
  content: { padding: space.md, gap: space.md },
});
'@
Write-RivalText 'mobile\src\ui\components\StateView.tsx' @'
// Pinta los 7 estados de una vista. Solo el estado "success" muestra el contenido real.

import type { ReactNode } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';

import type { ViewState } from '../../domain/viewState';
import { colors, font, radius, space } from '../theme';
import { PrimaryButton } from './PrimaryButton';

interface Props<T> {
  state: ViewState<T>;
  onRetry?: () => void;
  emptyAction?: { label: string; onPress: () => void };
  children: (data: T) => ReactNode;
}

const TITLES = {
  empty: 'Nada por aquí todavía',
  error: 'No pudimos cargar esto',
  offline: 'Sin conexión',
  conflict: 'Hay un cambio que revisar',
  approvalGate: 'Necesita aprobación',
} as const;

export function StateView<T>({ state, onRetry, emptyAction, children }: Props<T>) {
  if (state.kind === 'success') {
    return <>{children(state.data)}</>;
  }
  if (state.kind === 'loading') {
    return (
      <View style={styles.box} accessibilityLabel="Cargando" accessibilityLiveRegion="polite">
        <ActivityIndicator color={colors.accent} />
        <View style={styles.skeleton} />
        <View style={[styles.skeleton, styles.skeletonShort]} />
      </View>
    );
  }
  const tone =
    state.kind === 'error' ? colors.danger : state.kind === 'empty' ? colors.textMuted : colors.warning;
  return (
    <View style={[styles.box, { borderLeftColor: tone }]} accessibilityLiveRegion="polite">
      <Text style={styles.title}>{TITLES[state.kind]}</Text>
      <Text style={styles.message}>{state.message}</Text>
      {state.kind === 'error' && state.correlationId ? (
        <Text style={styles.code}>Código para soporte: {state.correlationId.slice(0, 12)}</Text>
      ) : null}
      {state.kind === 'empty' && emptyAction ? (
        <PrimaryButton label={emptyAction.label} onPress={emptyAction.onPress} />
      ) : null}
      {onRetry && state.kind !== 'empty' && state.kind !== 'approvalGate' ? (
        <PrimaryButton label="Reintentar" variant="secondary" onPress={onRetry} />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    gap: space.sm,
    padding: space.md,
    borderRadius: radius.md,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderLeftWidth: 4,
    borderLeftColor: colors.border,
  },
  title: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  message: { color: colors.textMuted, fontSize: font.body },
  code: { color: colors.textMuted, fontSize: font.small },
  skeleton: { height: 16, borderRadius: radius.sm, backgroundColor: colors.border },
  skeletonShort: { width: '60%' },
});
'@
Write-RivalText 'mobile\src\ui\components\TextField.tsx' @'
import { useState } from 'react';
import type { KeyboardTypeOptions } from 'react-native';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { colors, font, MIN_TOUCH, radius, space } from '../theme';

interface Props {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  error?: string;
  hint?: string;
  secure?: boolean;
  keyboardType?: KeyboardTypeOptions;
  placeholder?: string;
}

export function TextField({
  label,
  value,
  onChangeText,
  error,
  hint,
  secure = false,
  keyboardType,
  placeholder,
}: Props) {
  const [hidden, setHidden] = useState(secure);
  return (
    <View style={styles.wrapper}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.row}>
        <TextInput
          value={value}
          onChangeText={onChangeText}
          secureTextEntry={hidden}
          keyboardType={keyboardType}
          placeholder={placeholder}
          placeholderTextColor={colors.disabled}
          autoCapitalize={keyboardType === 'email-address' || secure ? 'none' : 'sentences'}
          autoCorrect={false}
          accessibilityLabel={label}
          accessibilityHint={error ?? hint}
          style={[styles.input, error ? styles.inputError : null]}
        />
        {secure ? (
          <Pressable
            onPress={() => setHidden((h) => !h)}
            accessibilityRole="button"
            accessibilityLabel={hidden ? 'Mostrar contraseña' : 'Ocultar contraseña'}
            style={styles.toggle}
          >
            <Text style={styles.toggleText}>{hidden ? 'Mostrar' : 'Ocultar'}</Text>
          </Pressable>
        ) : null}
      </View>
      {error ? (
        <Text style={styles.error} accessibilityLiveRegion="polite">
          {error}
        </Text>
      ) : hint ? (
        <Text style={styles.hint}>{hint}</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: space.xs },
  label: { color: colors.text, fontSize: font.small, fontWeight: '600' },
  row: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  input: {
    flex: 1,
    minHeight: MIN_TOUCH,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: space.md,
    backgroundColor: colors.surface,
    color: colors.text,
    fontSize: font.body,
  },
  inputError: { borderColor: colors.danger },
  toggle: { minHeight: MIN_TOUCH, justifyContent: 'center', paddingHorizontal: space.sm },
  toggleText: { color: colors.accent, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.small },
  hint: { color: colors.textMuted, fontSize: font.small },
});
'@
Write-RivalText 'mobile\src\ui\screens\CreateMatchRequestScreen.tsx' @'
import { StyleSheet, Text } from 'react-native';

import type { FormController, RequestForm } from '../../controllers/useMatchForms';
import { PLACE_LABEL, REFEREE_LABEL, SCOPE_LABEL } from '../../domain/matchLabels';
import type { PlaceKind, RefereeMode, SearchScope } from '../../domain/matchModels';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: FormController<RequestForm>;
  isChallenge: boolean;
  onBack: () => void;
}

const SCOPES: SearchScope[] = ['NEARBY', 'NEIGHBORHOOD', 'CITY'];
const REFEREES: RefereeMode[] = ['EITHER', 'WITH', 'WITHOUT'];
const PLACES: PlaceKind[] = ['TO_AGREE', 'INFORMAL', 'VENUE'];

export function CreateMatchRequestScreen({ controller, isChallenge, onBack }: Props) {
  const { form, handleChange, action } = controller;
  return (
    <Screen title={isChallenge ? 'Retar equipo' : 'Publicar búsqueda'} onBack={onBack}>
      <TextField
        label="Desde (dd/mm/aaaa hh:mm)"
        value={form.start}
        onChangeText={(v) => handleChange('start', v)}
      />
      <TextField
        label="Hasta (dd/mm/aaaa hh:mm)"
        value={form.end}
        onChangeText={(v) => handleChange('end', v)}
      />
      {!isChallenge ? (
        <ChoiceChips
          label="¿Quién puede verla?"
          selected={[form.scope]}
          choices={SCOPES.map((s) => ({ value: s, label: SCOPE_LABEL[s] }))}
          onToggle={(v) => handleChange('scope', v as SearchScope)}
        />
      ) : null}
      <ChoiceChips
        label="Árbitro"
        selected={[form.referee]}
        choices={REFEREES.map((r) => ({ value: r, label: REFEREE_LABEL[r] }))}
        onToggle={(v) => handleChange('referee', v as RefereeMode)}
      />
      <ChoiceChips
        label="Lugar"
        selected={[form.place]}
        choices={PLACES.map((p) => ({ value: p, label: PLACE_LABEL[p] }))}
        onToggle={(v) => handleChange('place', v as PlaceKind)}
      />
      <TextField
        label="Detalle del lugar (opcional)"
        value={form.placeNote}
        hint="Ej.: Parque del barrio, cancha de arena. Los pagos se acuerdan por fuera de la app."
        onChangeText={(v) => handleChange('placeNote', v)}
      />
      <TextField
        label="Mensaje (opcional)"
        value={form.message}
        onChangeText={(v) => handleChange('message', v)}
      />
      {controller.error ? <Text style={styles.error}>{controller.error}</Text> : null}
      {action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
      <PrimaryButton
        label={isChallenge ? 'Enviar reto' : 'Publicar'}
        loading={action.busy}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  error: { color: colors.danger, fontSize: font.body },
  message: { color: colors.text, fontSize: font.body },
});
'@
Write-RivalText 'mobile\src\ui\screens\CreateTeamScreen.tsx' @'
import { StyleSheet, Switch, Text, View } from 'react-native';

import type { CreateTeamController } from '../../controllers/useCreateTeamForm';
import type { Sport } from '../../domain/models';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font, space } from '../theme';

interface Props {
  controller: CreateTeamController;
  sports: Sport[];
  isCoach: boolean;
  onBack: () => void;
}

export function CreateTeamScreen({ controller, sports, isCoach, onBack }: Props) {
  const { form, errors } = controller;
  const modalities = sports.find((s) => s.code === form.sport)?.modalities ?? [];
  return (
    <Screen title="Crear equipo" onBack={onBack}>
      <TextField
        label="Nombre del equipo"
        value={form.name}
        error={errors.name}
        onChangeText={(v) => controller.handleText('name', v)}
      />
      <ChoiceChips
        label="Deporte"
        selected={form.sport ? [form.sport] : []}
        error={errors.sport}
        choices={sports.map((s) => ({ value: s.code, label: s.name }))}
        onToggle={controller.handleSport}
      />
      {modalities.length > 0 ? (
        <ChoiceChips
          label="Modalidad"
          selected={form.modality ? [form.modality] : []}
          error={errors.modality}
          choices={modalities.map((m) => ({ value: m.code, label: m.name }))}
          onToggle={controller.handleModality}
        />
      ) : null}
      <TextField
        label="Ciudad"
        value={form.city}
        error={errors.city}
        onChangeText={(v) => controller.handleText('city', v)}
      />
      <TextField
        label="Barrio donde juegan"
        value={form.neighborhood}
        error={errors.neighborhood}
        hint="Los rivales verán el barrio, nunca una ubicación exacta."
        onChangeText={(v) => controller.handleText('neighborhood', v)}
      />
      {isCoach ? (
        <View style={styles.switchRow}>
          <Text style={styles.switchLabel}>Entrar como DT (si no, entras como capitán)</Text>
          <Switch
            value={form.asCoach}
            onValueChange={controller.handleAsCoach}
            accessibilityLabel="Entrar como director técnico"
          />
        </View>
      ) : (
        <Text style={styles.note}>
          Entrarás como capitán y administrarás el equipo hasta que llegue un DT.
        </Text>
      )}
      {controller.submitError ? (
        <Text style={styles.error} accessibilityLiveRegion="assertive">
          {controller.submitError}
        </Text>
      ) : null}
      <PrimaryButton
        label="Crear equipo"
        loading={controller.submitting}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  switchRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: space.md },
  switchLabel: { flex: 1, color: colors.text, fontSize: font.body },
  note: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
});
'@
Write-RivalText 'mobile\src\ui\screens\FreeAgentPanelScreen.tsx' @'
import { StyleSheet, Switch, Text, View } from 'react-native';

import type { FreeAgentPanelController } from '../../controllers/useFreeAgentPanel';
import type { Sport } from '../../domain/models';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font, space } from '../theme';

interface Props {
  controller: FreeAgentPanelController;
  sports: Sport[];
  mySports: string[];
  onBack: () => void;
}

export function FreeAgentPanelScreen({ controller, sports, mySports, onBack }: Props) {
  const { action } = controller;
  return (
    <Screen title="Agente libre" onBack={onBack}>
      <Text style={styles.note}>
        Los DT de tu ciudad podrán encontrarte e invitarte. Solo verán tu nombre visible, posición y barrio.
      </Text>
      <StateView state={controller.profiles.state} onRetry={controller.profiles.handleReload}>
        {(profiles) =>
          mySports.map((code) => {
            const current = profiles.find((p) => p.sport_code === code);
            const name = sports.find((s) => s.code === code)?.name ?? code;
            return (
              <View key={code} style={styles.row}>
                <Text style={styles.label}>Disponible en {name}</Text>
                <Switch
                  value={current?.active ?? false}
                  disabled={action.busy}
                  onValueChange={(value) => void controller.handleToggle(code, value, current)}
                  accessibilityLabel={`Aparecer como agente libre en ${name}`}
                />
              </View>
            );
          })
        }
      </StateView>
      <Text style={styles.section} accessibilityRole="header">
        Invitaciones de equipos
      </Text>
      <StateView state={controller.invitations.state} onRetry={controller.invitations.handleReload}>
        {(items) =>
          items.map((invitation) => (
            <Card
              key={invitation.id}
              title={invitation.team.name}
              subtitle={`${invitation.team.modality_code} · ${invitation.team.neighborhood}, ${invitation.team.city}`}
            >
              {invitation.message ? <Text style={styles.label}>“{invitation.message}”</Text> : null}
              <PrimaryButton
                label="Aceptar"
                disabled={action.busy}
                onPress={() => void controller.handleRespond(invitation.id, true)}
              />
              <PrimaryButton
                label="Rechazar"
                variant="secondary"
                disabled={action.busy}
                onPress={() => void controller.handleRespond(invitation.id, false)}
              />
            </Card>
          ))
        }
      </StateView>
      {action.message ? (
        <Text style={styles.label} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  note: { color: colors.textMuted, fontSize: font.small },
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: space.md },
  label: { flex: 1, color: colors.text, fontSize: font.body },
  section: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
});
'@
Write-RivalText 'mobile\src\ui\screens\FreeAgentSearchScreen.tsx' @'
import { StyleSheet, Switch, Text, View } from 'react-native';

import type { FreeAgentSearchController } from '../../controllers/useScouting';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { LoadMore } from '../components/LoadMore';
import { StateView } from '../components/StateView';
import { colors, font, space } from '../theme';

interface Props {
  controller: FreeAgentSearchController;
  onBack: () => void;
}

export function FreeAgentSearchScreen({ controller, onBack }: Props) {
  const { action } = controller;
  return (
    <Screen title="Agentes libres" onBack={onBack}>
      <View style={styles.row}>
        <Text style={styles.label}>Solo de mi barrio</Text>
        <Switch
          value={controller.onlyMyNeighborhood}
          onValueChange={controller.handleOnlyNeighborhood}
          accessibilityLabel="Mostrar solo agentes libres de mi barrio"
        />
      </View>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(page) => (
          <>
            {page.items.map((agent) => (
              <Card
                key={agent.user_id}
                title={agent.display_name}
                subtitle={`${agent.position ?? 'Sin posición'} · ${agent.neighborhood}, ${agent.city}`}
              >
                {agent.note ? <Text style={styles.label}>{agent.note}</Text> : null}
                {controller.invited[agent.user_id] ? (
                  <Text style={styles.done}>Invitación enviada</Text>
                ) : (
                  <PrimaryButton
                    label="Invitar al equipo"
                    disabled={action.busy}
                    onPress={() => void controller.handleInvite(agent.user_id)}
                  />
                )}
              </Card>
            ))}
            <LoadMore
              hasMore={controller.hasMore}
              loading={controller.loadingMore}
              error={controller.moreError}
              onPress={() => void controller.handleLoadMore()}
            />
          </>
        )}
      </StateView>
      {action.message ? (
        <Text style={styles.label} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: space.md },
  label: { flex: 1, color: colors.text, fontSize: font.body },
  done: { color: colors.success, fontSize: font.small, fontWeight: '600' },
});
'@
Write-RivalText 'mobile\src\ui\screens\HomeScreen.tsx' @'
// Inicio según el rol. Lo que llega en Sprints futuros se rotula "Próximamente".

import { StyleSheet, Text } from 'react-native';

import { roleTitle, TEAM_ROLE_LABEL } from '../../domain/labels';
import type { MyTeam, User } from '../../domain/models';
import type { ViewState } from '../../domain/viewState';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  user: User;
  myTeams: ViewState<MyTeam[]>;
  onRefreshTeams: () => void;
  onSearchTeam: () => void;
  onCreateTeam: () => void;
  onFreeAgent: () => void;
  onOpenTeam: (teamId: number) => void;
  onLogout: () => void;
}

export function HomeScreen({
  user,
  myTeams,
  onRefreshTeams,
  onSearchTeam,
  onCreateTeam,
  onFreeAgent,
  onOpenTeam,
  onLogout,
}: Props) {
  const plays = user.roles.includes('PLAYER') || user.roles.includes('COACH');
  const hasTeam = myTeams.kind === 'success';
  return (
    <Screen title={`Hola, ${user.display_name}`}>
      <Text style={styles.lead}>
        {user.roles.map(roleTitle).join(' · ')} · {user.neighborhood}, {user.city}
      </Text>
      {plays ? (
        <>
          <Text style={styles.section} accessibilityRole="header">
            Mis equipos
          </Text>
          <StateView
            state={myTeams}
            onRetry={onRefreshTeams}
            emptyAction={{ label: 'Buscar equipo', onPress: onSearchTeam }}
          >
            {(teams) =>
              teams.map((item) => (
                <Card
                  key={item.team.id}
                  title={item.team.name}
                  subtitle={`${item.team.modality_code} · ${item.team.neighborhood}, ${item.team.city}`}
                  badge={item.is_admin ? 'Administras' : TEAM_ROLE_LABEL[item.my_role]}
                  onPress={() => onOpenTeam(item.team.id)}
                >
                  {item.is_admin && item.pending_requests > 0 ? (
                    <Text style={styles.pending}>{item.pending_requests} solicitud(es) por revisar</Text>
                  ) : null}
                </Card>
              ))
            }
          </StateView>
          <PrimaryButton label="Buscar equipo" variant="secondary" onPress={onSearchTeam} />
          <PrimaryButton label="Crear equipo" onPress={onCreateTeam} />
          <Card
            title="Agente libre e invitaciones"
            subtitle="Deja que los DT te encuentren y responde invitaciones"
            onPress={onFreeAgent}
          />
          {hasTeam ? <Card title="Ligas" subtitle="Buscar o crear liga · Próximamente (Sprint 3)" /> : null}
        </>
      ) : null}
      {user.roles.includes('REFEREE') ? (
        <Card title="Buscar liga" subtitle="Únete al cuerpo arbitral de una liga · Próximamente (Sprint 3)" />
      ) : null}
      {user.roles.includes('VENUE_OWNER') ? (
        <Card title="Mi establecimiento" subtitle="Registra canchas y horarios · Próximamente (Sprint 3)" />
      ) : null}
      <PrimaryButton label="Cerrar sesión" variant="secondary" onPress={onLogout} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  lead: { color: colors.textMuted, fontSize: font.body },
  section: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  pending: { color: colors.warning, fontSize: font.small, fontWeight: '600' },
});
'@
Write-RivalText 'mobile\src\ui\screens\LoginScreen.tsx' @'
import { StyleSheet, Text } from 'react-native';

import type { LoginController } from '../../controllers/useLoginForm';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: LoginController;
  onBack: () => void;
}

export function LoginScreen({ controller, onBack }: Props) {
  return (
    <Screen title="Iniciar sesión" onBack={onBack}>
      <TextField
        label="Correo"
        value={controller.email}
        keyboardType="email-address"
        onChangeText={controller.handleEmail}
      />
      <TextField
        label="Contraseña"
        value={controller.password}
        secure
        onChangeText={controller.handlePassword}
      />
      {controller.error ? (
        <Text style={styles.error} accessibilityLiveRegion="assertive">
          {controller.error}
        </Text>
      ) : null}
      <PrimaryButton
        label="Entrar"
        loading={controller.submitting}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  error: { color: colors.danger, fontSize: font.body },
});
'@
Write-RivalText 'mobile\src\ui\screens\MakeOfferScreen.tsx' @'
import { StyleSheet, Text } from 'react-native';

import type { FormController, OfferForm } from '../../controllers/useMatchForms';
import { formatLocal } from '../../domain/dateTime';
import { PLACE_LABEL, REFEREE_LABEL } from '../../domain/matchLabels';
import type { MatchRequest, PlaceKind } from '../../domain/matchModels';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: FormController<OfferForm>;
  request: MatchRequest;
  onBack: () => void;
}

const PLACES: PlaceKind[] = ['TO_AGREE', 'INFORMAL', 'VENUE'];

export function MakeOfferScreen({ controller, request, onBack }: Props) {
  const { form, handleChange, action } = controller;
  const refereeChoices: OfferForm['referee'][] =
    request.referee_mode === 'EITHER' ? ['WITHOUT', 'WITH'] : [request.referee_mode];
  return (
    <Screen title={`Oferta a ${request.team.name}`} onBack={onBack}>
      <Text style={styles.meta}>
        Juegan entre {formatLocal(request.window_start)} y {formatLocal(request.window_end)}.
      </Text>
      <TextField
        label="Fecha y hora propuesta (dd/mm/aaaa hh:mm)"
        value={form.start}
        onChangeText={(v) => handleChange('start', v)}
      />
      <ChoiceChips
        label="Árbitro"
        selected={[form.referee]}
        choices={refereeChoices.map((r) => ({ value: r, label: REFEREE_LABEL[r] }))}
        onToggle={(v) => handleChange('referee', v as OfferForm['referee'])}
      />
      <ChoiceChips
        label="Lugar"
        selected={[form.place]}
        choices={PLACES.map((p) => ({ value: p, label: PLACE_LABEL[p] }))}
        onToggle={(v) => handleChange('place', v as PlaceKind)}
      />
      <TextField
        label="Detalle del lugar"
        value={form.placeNote}
        onChangeText={(v) => handleChange('placeNote', v)}
      />
      <TextField
        label="Mensaje (opcional)"
        value={form.message}
        onChangeText={(v) => handleChange('message', v)}
      />
      {controller.error ? <Text style={styles.error}>{controller.error}</Text> : null}
      {action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {action.message}
        </Text>
      ) : null}
      <PrimaryButton
        label="Enviar oferta"
        loading={action.busy}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
  error: { color: colors.danger, fontSize: font.body },
  message: { color: colors.text, fontSize: font.body },
});
'@
Write-RivalText 'mobile\src\ui\screens\MatchFeedScreen.tsx' @'
import type { FeedController } from '../../controllers/useMatches';
import { formatLocal } from '../../domain/dateTime';
import { PLACE_LABEL, REFEREE_LABEL, SCOPE_LABEL, distanceText } from '../../domain/matchLabels';
import type { MatchRequest, SearchScope } from '../../domain/matchModels';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';

interface Props {
  controller: FeedController;
  isAdmin: boolean;
  onOffer: (request: MatchRequest) => void;
  onMyOffers: (request: MatchRequest) => void;
  onBack: () => void;
}

const SCOPES: SearchScope[] = ['NEARBY', 'NEIGHBORHOOD', 'CITY'];

export function MatchFeedScreen({ controller, isAdmin, onOffer, onMyOffers, onBack }: Props) {
  return (
    <Screen title="Partidos para mi equipo" onBack={onBack}>
      <ChoiceChips
        label="Alcance"
        selected={[controller.scope]}
        choices={SCOPES.map((s) => ({ value: s, label: SCOPE_LABEL[s] }))}
        onToggle={(v) => controller.handleScope(v as SearchScope)}
      />
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((request) => (
            <Card
              key={request.id}
              title={request.team.name}
              subtitle={`${request.team.neighborhood} ${distanceText(request.distance_band)} · ${formatLocal(request.window_start)} → ${formatLocal(request.window_end)} · ${REFEREE_LABEL[request.referee_mode]} · ${PLACE_LABEL[request.place_kind]}`}
              badge={request.target_team_id ? 'Te retaron' : undefined}
            >
              {isAdmin ? <PrimaryButton label="Hacer oferta" onPress={() => onOffer(request)} /> : null}
              <PrimaryButton label="Ver mi oferta" variant="secondary" onPress={() => onMyOffers(request)} />
            </Card>
          ))
        }
      </StateView>
    </Screen>
  );
}
'@
Write-RivalText 'mobile\src\ui\screens\MatchRequestsScreen.tsx' @'
import { Alert, StyleSheet, Text } from 'react-native';

import type { MyRequestsController } from '../../controllers/useMatches';
import { formatLocal } from '../../domain/dateTime';
import { PLACE_LABEL, REFEREE_LABEL, REQUEST_STATUS_LABEL, SCOPE_LABEL } from '../../domain/matchLabels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: MyRequestsController;
  isAdmin: boolean;
  onCreate: () => void;
  onOpenOffers: (requestId: number, open: boolean) => void;
  onBack: () => void;
}

export function MatchRequestsScreen({ controller, isAdmin, onCreate, onOpenOffers, onBack }: Props) {
  const confirmCancel = (requestId: number) =>
    Alert.alert('¿Cancelar la búsqueda?', 'Las ofertas pendientes también se cancelarán.', [
      { text: 'No', style: 'cancel' },
      {
        text: 'Cancelar búsqueda',
        style: 'destructive',
        onPress: () => void controller.handleCancel(requestId),
      },
    ]);
  return (
    <Screen title="Búsquedas de partido" onBack={onBack}>
      {isAdmin ? <PrimaryButton label="Publicar búsqueda" onPress={onCreate} /> : null}
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(items) =>
          items.map((request) => (
            <Card
              key={request.id}
              title={`${formatLocal(request.window_start)} → ${formatLocal(request.window_end)}`}
              subtitle={`${request.target_team_id ? 'Reto directo' : SCOPE_LABEL[request.scope]} · ${REFEREE_LABEL[request.referee_mode]} · ${PLACE_LABEL[request.place_kind]}`}
              badge={REQUEST_STATUS_LABEL[request.status]}
            >
              <Text style={styles.meta}>{request.pending_offers} oferta(s) pendiente(s)</Text>
              <PrimaryButton
                label="Ver ofertas"
                variant="secondary"
                onPress={() => onOpenOffers(request.id, request.status === 'OPEN')}
              />
              {isAdmin && request.status === 'OPEN' ? (
                <PrimaryButton
                  label="Cancelar búsqueda"
                  variant="danger"
                  disabled={controller.action.busy}
                  onPress={() => confirmCancel(request.id)}
                />
              ) : null}
            </Card>
          ))
        }
      </StateView>
      {controller.action.message ? <Text style={styles.meta}>{controller.action.message}</Text> : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
});
'@
Write-RivalText 'mobile\src\ui\screens\OffersScreen.tsx' @'
import { Alert, StyleSheet, Text } from 'react-native';

import type { OffersController } from '../../controllers/useMatches';
import { formatLocal } from '../../domain/dateTime';
import { OFFER_STATUS_LABEL, PLACE_LABEL, REFEREE_LABEL } from '../../domain/matchLabels';
import type { Offer } from '../../domain/matchModels';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: OffersController;
  isRequestAdmin: boolean;
  myTeamIds: number[];
  requestOpen: boolean;
  onBack: () => void;
}

export function OffersScreen({ controller, isRequestAdmin, myTeamIds, requestOpen, onBack }: Props) {
  const busy = controller.action.busy;
  const canAct = (offer: Offer) => requestOpen && offer.status === 'PENDING';
  const confirmAccept = (offer: Offer) =>
    Alert.alert(`¿Jugar contra ${offer.team.name}?`, 'Las demás ofertas quedarán reemplazadas.', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Aceptar', onPress: () => void controller.handleDecide(offer.id, 'accept') },
    ]);
  return (
    <Screen title="Ofertas" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(offers) =>
          offers.map((offer) => (
            <Card
              key={offer.id}
              title={`${offer.team.name} · ${formatLocal(offer.proposed_start)}`}
              subtitle={`${REFEREE_LABEL[offer.referee_mode]} · ${PLACE_LABEL[offer.place_kind]}${offer.place_note ? ` · ${offer.place_note}` : ''}`}
              badge={`${OFFER_STATUS_LABEL[offer.status]}${offer.version > 1 ? ` · v${offer.version}` : ''}`}
            >
              {offer.message ? <Text style={styles.meta}>“{offer.message}”</Text> : null}
              {isRequestAdmin && canAct(offer) ? (
                <>
                  <PrimaryButton label="Aceptar" disabled={busy} onPress={() => confirmAccept(offer)} />
                  <PrimaryButton
                    label="Rechazar"
                    variant="secondary"
                    disabled={busy}
                    onPress={() => void controller.handleDecide(offer.id, 'reject')}
                  />
                </>
              ) : null}
              {!isRequestAdmin && canAct(offer) && myTeamIds.includes(offer.team.id) ? (
                <PrimaryButton
                  label="Retirar oferta"
                  variant="secondary"
                  disabled={busy}
                  onPress={() => void controller.handleDecide(offer.id, 'withdraw')}
                />
              ) : null}
            </Card>
          ))
        }
      </StateView>
      {controller.action.message ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  meta: { color: colors.textMuted, fontSize: font.small },
  message: { color: colors.text, fontSize: font.body },
});
'@
Write-RivalText 'mobile\src\ui\screens\RegisterScreen.tsx' @'
import { StyleSheet, Text } from 'react-native';

import type { RegistrationController } from '../../controllers/useRegistrationForm';
import { roleTitle } from '../../domain/labels';
import type { Sport } from '../../domain/models';
import type { ViewState } from '../../domain/viewState';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: RegistrationController;
  catalog: ViewState<Sport[]>;
  onRetryCatalog: () => void;
  onBack: () => void;
}

export function RegisterScreen({ controller, catalog, onRetryCatalog, onBack }: Props) {
  const { form, errors } = controller;
  const plays = form.role === 'PLAYER' || form.role === 'COACH';
  return (
    <Screen title={`Registro: ${roleTitle(form.role)}`} onBack={onBack}>
      <TextField
        label="Nombre visible"
        value={form.displayName}
        error={errors.displayName}
        onChangeText={(v) => controller.handleChange('displayName', v)}
      />
      <TextField
        label="Correo"
        value={form.email}
        error={errors.email}
        keyboardType="email-address"
        onChangeText={(v) => controller.handleChange('email', v)}
      />
      <TextField
        label="Contraseña"
        value={form.password}
        error={errors.password}
        secure
        hint="Mínimo 10 caracteres. Puedes pegarla desde tu gestor de contraseñas."
        onChangeText={(v) => controller.handleChange('password', v)}
      />
      <TextField
        label="Fecha de nacimiento"
        value={form.birthDate}
        error={errors.birthDate}
        placeholder="dd/mm/aaaa"
        keyboardType="numbers-and-punctuation"
        hint="RIVAL es solo para mayores de 18 años."
        onChangeText={(v) => controller.handleChange('birthDate', v)}
      />
      <StateView state={catalog} onRetry={onRetryCatalog}>
        {(sports) => (
          <ChoiceChips
            label="¿Para qué deportes?"
            selected={form.sports}
            error={errors.sports}
            choices={sports.map((s) => ({ value: s.code, label: s.name }))}
            onToggle={controller.handleToggleSport}
          />
        )}
      </StateView>
      <TextField
        label="Ciudad"
        value={form.city}
        error={errors.city}
        onChangeText={(v) => controller.handleChange('city', v)}
      />
      <TextField
        label="Barrio"
        value={form.neighborhood}
        error={errors.neighborhood}
        hint="Solo se muestra tu barrio, nunca tu ubicación exacta."
        onChangeText={(v) => controller.handleChange('neighborhood', v)}
      />
      {plays ? (
        <TextField
          label="Posición (opcional)"
          value={form.position}
          onChangeText={(v) => controller.handleChange('position', v)}
        />
      ) : null}
      {controller.submitError ? (
        <Text style={styles.error} accessibilityLiveRegion="assertive">
          {controller.submitError}
        </Text>
      ) : null}
      <PrimaryButton
        label="Crear cuenta"
        loading={controller.submitting}
        onPress={() => void controller.handleSubmit()}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  error: { color: colors.danger, fontSize: font.body },
});
'@
Write-RivalText 'mobile\src\ui\screens\RivalSearchScreen.tsx' @'
import { StyleSheet, Text } from 'react-native';

import type { RivalSearchController } from '../../controllers/useScouting';
import { SCOPE_LABEL, distanceText } from '../../domain/matchLabels';
import type { SearchScope } from '../../domain/matchModels';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { LoadMore } from '../components/LoadMore';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: RivalSearchController;
  canChallenge: boolean;
  onChallenge: (teamId: number) => void;
  onBack: () => void;
}

const SCOPES: SearchScope[] = ['NEARBY', 'NEIGHBORHOOD', 'CITY'];
const RADII = [2, 5, 10, 15];

export function RivalSearchScreen({ controller, canChallenge, onChallenge, onBack }: Props) {
  return (
    <Screen title="Buscar rival" onBack={onBack}>
      <Text style={styles.note}>
        Solo se muestran barrios y distancias aproximadas, nunca ubicaciones exactas.
      </Text>
      <ChoiceChips
        label="Alcance"
        selected={[controller.scope]}
        choices={SCOPES.map((s) => ({ value: s, label: SCOPE_LABEL[s] }))}
        onToggle={(value) => controller.handleScope(value as SearchScope)}
      />
      {controller.scope === 'NEARBY' ? (
        <ChoiceChips
          label="Radio"
          selected={[String(controller.radiusKm)]}
          choices={RADII.map((km) => ({ value: String(km), label: `${km} km` }))}
          onToggle={(value) => controller.handleRadius(Number(value))}
        />
      ) : null}
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(page) => (
          <>
            {page.items.map((rival) => (
              <Card
                key={rival.team.id}
                title={rival.team.name}
                subtitle={`${rival.team.neighborhood}, ${rival.team.city} ${distanceText(rival.distance_band)} · ${rival.team.member_count} jugador(es)`}
                badge={rival.team.has_coach ? 'Con DT' : 'Sin DT'}
              >
                {canChallenge ? (
                  <PrimaryButton
                    label="Retar"
                    variant="secondary"
                    onPress={() => onChallenge(rival.team.id)}
                  />
                ) : null}
              </Card>
            ))}
            <LoadMore
              hasMore={controller.hasMore}
              loading={controller.loadingMore}
              error={controller.moreError}
              onPress={() => void controller.handleLoadMore()}
            />
          </>
        )}
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  note: { color: colors.textMuted, fontSize: font.small },
});
'@
Write-RivalText 'mobile\src\ui\screens\RolePickerScreen.tsx' @'
import { StyleSheet, Text } from 'react-native';

import { ROLE_OPTIONS } from '../../domain/labels';
import type { UserRole } from '../../domain/models';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { colors, font } from '../theme';

interface Props {
  onPickRole: (role: UserRole) => void;
  onLogin: () => void;
}

export function RolePickerScreen({ onPickRole, onLogin }: Props) {
  return (
    <Screen title="Bienvenido a RIVAL">
      <Text style={styles.lead}>
        ¿Cómo quieres registrarte? Luego puedes agregar otro rol desde tu perfil.
      </Text>
      {ROLE_OPTIONS.map((option) => (
        <Card
          key={option.role}
          title={option.title}
          subtitle={option.description}
          onPress={() => onPickRole(option.role)}
        />
      ))}
      <PrimaryButton label="Ya tengo cuenta" variant="secondary" onPress={onLogin} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  lead: { color: colors.textMuted, fontSize: font.body },
});
'@
Write-RivalText 'mobile\src\ui\screens\TeamScreen.tsx' @'
// Mi equipo: plantilla, administrador y solicitudes. Salir pide confirmación.

import type { ReactNode } from 'react';
import { Alert, StyleSheet, Text } from 'react-native';

import type { TeamDetailController } from '../../controllers/useTeamDetail';
import { TEAM_ROLE_LABEL } from '../../domain/labels';
import type { TeamSummary } from '../../domain/models';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: TeamDetailController;
  renderActions?: (team: TeamSummary, isAdmin: boolean) => ReactNode;
  userId: number;
  onBack: () => void;
}

export function TeamScreen({ controller, userId, renderActions, onBack }: Props) {
  const myRole =
    controller.detail.kind === 'success'
      ? controller.detail.data.members.find((m) => m.user_id === userId)?.role
      : undefined;
  const confirmCaptain = (memberId: number, name: string) => {
    if (myRole !== 'CAPTAIN') {
      void controller.handleSetCaptain(memberId);
      return;
    }
    Alert.alert(
      '¿Pasar la capitanía?',
      `${name} será el capitán y administrará el equipo. Tú pasas a jugador.`,
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Confirmar', onPress: () => void controller.handleSetCaptain(memberId) },
      ],
    );
  };
  const confirmLeave = () =>
    Alert.alert('¿Salir del equipo?', 'Dejarás de ver sus partidos y convocatorias.', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Salir', style: 'destructive', onPress: () => void controller.handleLeave() },
    ]);
  return (
    <Screen title="Mi equipo" onBack={onBack}>
      <StateView state={controller.detail} onRetry={controller.handleRefresh}>
        {(detail) => (
          <>
            <Text style={styles.teamName} accessibilityRole="header">
              {detail.team.name}
            </Text>
            <Text style={styles.meta}>
              {detail.team.modality_code} · {detail.team.neighborhood}, {detail.team.city}
            </Text>
            {renderActions?.(detail.team, controller.isAdmin)}
            <Text style={styles.section} accessibilityRole="header">
              Plantilla ({detail.members.length})
            </Text>
            {detail.members.map((member) => (
              <Card
                key={member.user_id}
                title={member.user_id === userId ? `${member.display_name} (tú)` : member.display_name}
                subtitle={member.position ?? undefined}
                badge={
                  member.user_id === detail.admin_user_id
                    ? `${TEAM_ROLE_LABEL[member.role]} · Admin`
                    : TEAM_ROLE_LABEL[member.role]
                }
              >
                {controller.isAdmin && member.role === 'PLAYER' ? (
                  <PrimaryButton
                    label="Nombrar capitán"
                    variant="secondary"
                    disabled={controller.busy}
                    onPress={() => confirmCaptain(member.user_id, member.display_name)}
                  />
                ) : null}
              </Card>
            ))}
          </>
        )}
      </StateView>
      {controller.isAdmin ? (
        <>
          <Text style={styles.section} accessibilityRole="header">
            Solicitudes para unirse
          </Text>
          <StateView state={controller.requests} onRetry={controller.handleRefresh}>
            {(requests) =>
              requests.map((request) => (
                <Card
                  key={request.id}
                  title={request.display_name}
                  subtitle={
                    request.desired_role === 'COACH'
                      ? 'Quiere entrar como DT. Si lo aceptas, el DT pasa a administrar el equipo.'
                      : `Quiere entrar como ${TEAM_ROLE_LABEL[request.desired_role]}`
                  }
                >
                  <PrimaryButton
                    label="Aceptar"
                    disabled={controller.busy}
                    onPress={() => void controller.handleDecide(request.id, true)}
                  />
                  <PrimaryButton
                    label="Rechazar"
                    variant="secondary"
                    disabled={controller.busy}
                    onPress={() => void controller.handleDecide(request.id, false)}
                  />
                </Card>
              ))
            }
          </StateView>
        </>
      ) : null}
      {controller.actionMessage ? (
        <Text style={styles.message} accessibilityLiveRegion="polite">
          {controller.actionMessage}
        </Text>
      ) : null}
      <PrimaryButton
        label="Salir del equipo"
        variant="danger"
        loading={controller.busy}
        onPress={confirmLeave}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  teamName: { color: colors.text, fontSize: font.title, fontWeight: '700' },
  meta: { color: colors.textMuted, fontSize: font.body },
  section: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  message: { color: colors.text, fontSize: font.body },
});
'@
Write-RivalText 'mobile\src\ui\screens\TeamSearchScreen.tsx' @'
import { StyleSheet, Text } from 'react-native';

import type { TeamSearchController } from '../../controllers/useTeamSearch';
import type { Sport, TeamSummary } from '../../domain/models';
import { Card } from '../components/Card';
import { ChoiceChips } from '../components/ChoiceChips';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font } from '../theme';

interface Props {
  controller: TeamSearchController;
  sports: Sport[];
  canJoinAsCoach: boolean;
  onCreateTeam: () => void;
  onBack: () => void;
}

export function TeamSearchScreen({ controller, sports, canJoinAsCoach, onCreateTeam, onBack }: Props) {
  const sportName = (code: string) => sports.find((s) => s.code === code)?.name ?? code;
  const renderJoin = (team: TeamSummary) => {
    const status = controller.joinStatus[team.id];
    if (status?.kind === 'sent') {
      return (
        <Text style={styles.sent} accessibilityLiveRegion="polite">
          {status.message}
        </Text>
      );
    }
    return (
      <>
        {status?.kind === 'failed' ? <Text style={styles.failed}>{status.message}</Text> : null}
        <PrimaryButton
          label="Solicitar unirme"
          loading={status?.kind === 'sending'}
          onPress={() => void controller.handleRequestJoin(team.id, 'PLAYER')}
        />
        {canJoinAsCoach && !team.has_coach ? (
          <PrimaryButton
            label="Unirme como DT"
            variant="secondary"
            disabled={status?.kind === 'sending'}
            onPress={() => void controller.handleRequestJoin(team.id, 'COACH')}
          />
        ) : null}
      </>
    );
  };
  return (
    <Screen title="Buscar equipo" onBack={onBack}>
      <ChoiceChips
        label="Deporte"
        selected={controller.sport ? [controller.sport] : []}
        choices={sports.map((s) => ({ value: s.code, label: s.name }))}
        onToggle={(code) => controller.handleSport(controller.sport === code ? null : code)}
      />
      <TextField label="Ciudad" value={controller.city} onChangeText={controller.handleCity} />
      <TextField
        label="Nombre del equipo (opcional)"
        value={controller.text}
        onChangeText={controller.handleText}
      />
      <PrimaryButton label="Buscar" variant="secondary" onPress={controller.handleSearch} />
      <StateView
        state={controller.state}
        onRetry={controller.handleSearch}
        emptyAction={{ label: 'Crear mi equipo', onPress: onCreateTeam }}
      >
        {(page) => (
          <>
            <Text style={styles.count}>{page.total} equipo(s) encontrados</Text>
            {page.items.map((team) => (
              <Card
                key={team.id}
                title={team.name}
                subtitle={`${sportName(team.sport_code)} ${team.modality_code} · ${team.neighborhood}, ${team.city} · ${team.member_count} jugador(es)`}
                badge={team.has_coach ? 'Con DT' : 'Sin DT'}
              >
                {renderJoin(team)}
              </Card>
            ))}
            {controller.hasMore ? (
              <PrimaryButton
                label="Cargar más"
                variant="secondary"
                loading={controller.loadingMore}
                onPress={() => void controller.handleLoadMore()}
              />
            ) : null}
          </>
        )}
      </StateView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  count: { color: colors.textMuted, fontSize: font.small },
  sent: { color: colors.success, fontSize: font.small, fontWeight: '600' },
  failed: { color: colors.danger, fontSize: font.small },
});
'@
Write-RivalText 'mobile\src\ui\theme.ts' @'
// Tokens de diseño: escala Slate, un solo color de acento y colores de estado con significado.

export const colors = {
  background: '#F8FAFC',
  surface: '#FFFFFF',
  border: '#E2E8F0',
  text: '#0F172A',
  textMuted: '#475569',
  accent: '#1D4ED8',
  accentText: '#FFFFFF',
  success: '#15803D',
  warning: '#B45309',
  danger: '#B91C1C',
  disabled: '#94A3B8',
} as const;

export const space = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 } as const;

export const radius = { sm: 8, md: 12 } as const;

export const font = {
  title: 24,
  heading: 18,
  body: 16,
  small: 14,
} as const;

// Objetivo táctil mínimo recomendado para accesibilidad.
export const MIN_TOUCH = 44;
'@
Write-RivalText 'mobile\tests\dateTime.test.ts' @'
// Ejecutar: node --experimental-strip-types --test tests/dateTime.test.ts
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { formatLocal, localTextInDays, parseLocalDateTime } from '../src/domain/dateTime.ts';
import { DISTANCE_LABEL } from '../src/domain/matchLabels.ts';

test('fecha y hora locales se envían con zona de Colombia', () => {
  assert.equal(parseLocalDateTime('28/11/2026 18:30'), '2026-11-28T18:30:00-05:00');
  assert.equal(parseLocalDateTime('5/11/2026 18:30'), null);
  assert.equal(parseLocalDateTime('31/11/2026 10:00'), null);
  assert.equal(parseLocalDateTime('28/11/2026 24:00'), null);
});

test('formatea en hora de Colombia aunque llegue en UTC', () => {
  assert.equal(formatLocal('2026-11-28T23:30:00Z'), 'sáb 28/11 18:30');
  assert.equal(formatLocal('2026-11-29T02:00:00+00:00'), 'sáb 28/11 21:00');
});

test('cambio de año al sumar días', () => {
  assert.equal(localTextInDays(new Date('2026-12-31T15:00:00Z'), 1, 9), '01/01/2027 09:00');
});

test('los rangos de distancia nunca muestran un punto exacto', () => {
  assert.deepEqual(Object.values(DISTANCE_LABEL), ['a menos de 2 km', 'a 2–5 km', 'a más de 5 km']);
});
'@
Write-RivalText 'mobile\tests\validation.test.ts' @'
// Pruebas de las reglas locales. Ejecutar: node --experimental-strip-types --test tests/
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { isAdult, parseBirthDate, validateRegistration } from '../src/domain/validation.ts';

const today = new Date(2026, 10, 23);

test('cumple 18 el día de su cumpleaños', () => {
  assert.equal(isAdult('2008-11-23', today), true);
  assert.equal(isAdult('2008-11-24', today), false);
});

test('29 de febrero cumple el 1 de marzo en año no bisiesto', () => {
  assert.equal(isAdult('2008-02-29', new Date(2026, 1, 28)), false);
  assert.equal(isAdult('2008-02-29', new Date(2026, 2, 1)), true);
});

test('fecha inexistente se rechaza', () => {
  assert.equal(parseBirthDate('31/02/2000'), null);
  assert.equal(parseBirthDate('05/10/1998'), '1998-10-05');
});

test('formulario de menor muestra el mensaje de edad', () => {
  const errors = validateRegistration(
    {
      role: 'PLAYER',
      displayName: 'José Peña',
      email: 'jose@rival.test',
      password: 'mi equipo juega los sábados',
      birthDate: '01/01/2012',
      sports: ['FOOTBALL'],
      city: 'Barranquilla',
      neighborhood: 'El Prado',
      position: '',
    },
    today,
  );
  assert.equal(errors.birthDate, 'Por ahora RIVAL es solo para mayores de 18 años.');
  assert.equal(errors.displayName, undefined);
});
'@
Write-RivalText 'mobile\tsconfig.json' @'
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "verbatimModuleSyntax": true,
    "noUncheckedIndexedAccess": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "allowImportingTsExtensions": true,
    "types": [
      "node"
    ]
  }
}
'@

Write-Host ''
Write-Host "Archivos creados: $($Created.Count) | reemplazados (con .bak): $($Replaced.Count) | sin cambios: $($Unchanged.Count)" -ForegroundColor Green
foreach ($R in $Replaced) { Write-Host "  reemplazado: $R  (copia en $R.bak-$Stamp)" }

# Revision de 150 lineas por archivo de codigo
$Long = Get-ChildItem -Path (Join-Path $RepoPath 'backend\app'), (Join-Path $RepoPath 'backend\tests'), (Join-Path $RepoPath 'mobile\src') -Recurse -Include *.py, *.ts, *.tsx |
  Where-Object { $_.FullName -notmatch '__pycache__' } |
  ForEach-Object { $N = @(Get-Content -LiteralPath $_.FullName).Count; if ($N -gt 150) { "$($_.FullName): $N lineas (EXCEDE 150)" } }
if ($Long) { $Long | ForEach-Object { Write-Host $_ -ForegroundColor Red } } else { Write-Host 'Lineas por archivo: ninguno pasa de 150.' -ForegroundColor Green }

Write-Host ''
Write-Host 'El siguiente paso instala dependencias desde internet:' -ForegroundColor Yellow
Write-Host '  - backend: crea backend\venv (si no existe) e instala backend\requirements-dev.txt desde PyPI'
Write-Host '  - mobile:  npm ci (paquetes exactos de mobile\package-lock.json desde npm)'
$Answer = Read-Host 'Instalar dependencias y ejecutar las pruebas ahora? (s/n)'
if ($Answer -notmatch '^[sS]') {
  Write-Host 'Listo. Pruebas NO EJECUTADAS. Puedes correrlas despues con los comandos de README.md.' -ForegroundColor Yellow
  return
}

$Results = [ordered]@{}
Push-Location (Join-Path $RepoPath 'backend')
try {
  if (-not (Test-Path '.\venv\Scripts\python.exe')) {
    if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m venv venv } else { & python -m venv venv }
  }
  & .\venv\Scripts\python.exe -m pip install --disable-pip-version-check -q -r requirements-dev.txt
  & .\venv\Scripts\python.exe -m pytest -q
  $Results['backend pytest'] = if ($LASTEXITCODE -eq 0) { 'APROBADO' } else { "FALLIDO (codigo $LASTEXITCODE)" }
} catch {
  $Results['backend pytest'] = "NO EJECUTADO: $($_.Exception.Message)"
} finally { Pop-Location }

Push-Location (Join-Path $RepoPath 'mobile')
try {
  & npm ci --no-audit --no-fund
  & npm run typecheck
  $Results['mobile tsc --noEmit'] = if ($LASTEXITCODE -eq 0) { 'APROBADO' } else { "FALLIDO (codigo $LASTEXITCODE)" }
  & npm test
  $Results['mobile npm test'] = if ($LASTEXITCODE -eq 0) { 'APROBADO' } else { "FALLIDO (codigo $LASTEXITCODE)" }
} catch {
  $Results['mobile'] = "NO EJECUTADO: $($_.Exception.Message)"
} finally { Pop-Location }

Write-Host ''
Write-Host '===== Resumen del Sprint =====' -ForegroundColor Cyan
foreach ($K in $Results.Keys) { Write-Host ("{0,-22} {1}" -f $K, $Results[$K]) }
Write-Host 'Revisa con "git status" y, si todo esta bien, haz commit y push tu mismo.'
