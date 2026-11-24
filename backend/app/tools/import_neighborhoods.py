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
