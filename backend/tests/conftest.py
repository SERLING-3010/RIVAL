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
