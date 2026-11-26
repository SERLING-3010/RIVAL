"""Punto de entrada de la API de RIVAL.

Desarrollo local:  uvicorn app.main:app --host 127.0.0.1 --port 8000
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_account, routes_achievements, routes_auth, routes_chat, routes_checkin, routes_contracts, routes_cup,
    routes_goal_claims, routes_league_matches, routes_leagues, routes_loans, routes_manager, routes_matchday,
    routes_matches, routes_moderation, routes_pending, routes_push, routes_scouting, routes_squad,
    routes_suggestions, routes_tactics, routes_teams, routes_venues,
)
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
    app.include_router(routes_account.router)
    app.include_router(routes_achievements.router)
    app.include_router(routes_teams.router)
    app.include_router(routes_scouting.router)
    app.include_router(routes_suggestions.router)
    app.include_router(routes_squad.router)
    app.include_router(routes_goal_claims.router)
    app.include_router(routes_push.router)
    app.include_router(routes_tactics.router)
    app.include_router(routes_matches.router)
    app.include_router(routes_contracts.router)
    app.include_router(routes_leagues.router)
    app.include_router(routes_venues.router)
    app.include_router(routes_manager.router)
    app.include_router(routes_league_matches.router)
    app.include_router(routes_matchday.router)
    app.include_router(routes_pending.router)
    app.include_router(routes_moderation.router)
    app.include_router(routes_loans.router)
    app.include_router(routes_chat.router)
    app.include_router(routes_checkin.router)
    app.include_router(routes_cup.router)
    return app


app = create_app()
