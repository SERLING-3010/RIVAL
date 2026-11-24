"""Nombra moderadora a una persona registrada. Solo por línea de comandos (Sprint 12).

Uso:  python -m app.tools.grant_moderator correo@ejemplo.com
Usa RIVAL_DATABASE_URL igual que la API. Queda en la auditoría como AUTOMATION.
"""

import sys
from datetime import timedelta

from app.domain.sports_catalog import SportCatalog
from app.persistence.database import make_engine, make_session_factory, session_scope
from app.services import sanction_service
from app.services.clock import SystemClock
from app.services.context import ServiceContext
from app.settings import Settings


def main(email: str) -> None:
    settings = Settings()
    for session in session_scope(make_session_factory(make_engine(settings.database_url))):
        ctx = ServiceContext(db=session, clock=SystemClock(), catalog=SportCatalog.load(settings.catalog_path),
                             session_ttl=timedelta(0), session_idle=timedelta(0))
        user = sanction_service.grant_moderator(ctx, email)
        print(f"Moderadora: {user.display_name} (id {user.id})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python -m app.tools.grant_moderator correo@ejemplo.com")
    main(sys.argv[1])
