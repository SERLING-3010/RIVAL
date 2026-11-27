"""Borra las sesiones vencidas o inactivas. Pensado para una tarea programada diaria.

Uso:  python -m app.tools.purge_sessions
Usa RIVAL_DATABASE_URL igual que la API. Queda registrado en la auditoría como SYSTEM_RULE.
"""

from app.domain.sports_catalog import SportCatalog
from app.persistence.database import make_engine, make_session_factory, session_scope
from app.services import security_service
from app.services.clock import SystemClock
from app.services.context import ServiceContext
from app.settings import Settings


def main() -> None:
    settings = Settings()
    engine = make_engine(settings.database_url)
    for session in session_scope(make_session_factory(engine)):
        ctx = ServiceContext(db=session, clock=SystemClock(), catalog=SportCatalog.load(settings.catalog_path),
                             session_ttl=settings.session_ttl, session_idle=settings.session_idle)
        print(f"Sesiones borradas: {security_service.purge_sessions(ctx)}")


if __name__ == "__main__":
    main()
