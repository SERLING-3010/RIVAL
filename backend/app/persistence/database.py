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
        models_chat,
        models_contracts,
        models_identity,
        models_league_matches,
        models_leagues,
        models_manager,
        models_matchday,
        models_matches,
        models_moderation,
        models_places,
        models_results,
        models_scouting,
        models_teams,
        models_venues,
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
