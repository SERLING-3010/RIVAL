"""Centro de salud: revisa los invariantes y termina con código 1 si hay hallazgos S0 o S1.

Uso:  python -m app.tools.health_check
Usa RIVAL_DATABASE_URL igual que la API. Solo lee; no cambia nada.
"""

from datetime import timedelta

from app.domain.sports_catalog import SportCatalog
from app.persistence.database import make_engine, make_session_factory
from app.services import health_service
from app.services.clock import SystemClock
from app.services.context import ServiceContext
from app.settings import Settings


def main() -> int:
    settings = Settings()
    engine = make_engine(settings.database_url)
    with make_session_factory(engine)() as session:
        ctx = ServiceContext(db=session, clock=SystemClock(), catalog=SportCatalog.load(settings.catalog_path),
                             session_ttl=timedelta(0), session_idle=timedelta(0))
        findings = health_service.run_checks(ctx)
        session.rollback()
    for f in findings:
        print(f"[{f.severity}] {f.code} {f.entity}#{f.entity_id or '-'}: {f.message}")
    print(f"Hallazgos: {len(findings)}")
    return 1 if any(f.severity in ("S0", "S1") for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
