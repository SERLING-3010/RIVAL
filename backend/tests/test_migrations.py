"""Las migraciones de Alembic producen exactamente el esquema de los modelos (Sprint 9).

Si alguien cambia un modelo sin crear la migración, esta prueba falla en el CI.
"""

from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.database import Base, load_models, make_engine
from app.persistence.models_audit import AuditHead

BACKEND = Path(__file__).resolve().parents[1]


def test_upgrade_head_matches_models(tmp_path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'migrated.db').as_posix()}"
    monkeypatch.setenv("RIVAL_DATABASE_URL", url)
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "migrations"))
    command.upgrade(config, "head")
    engine = make_engine(url)
    load_models()
    with engine.connect() as connection:
        diff = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    with Session(engine) as session:
        head = session.scalar(select(AuditHead).where(AuditHead.id == 1))
    engine.dispose()
    assert diff == [], f"Hay cambios en los modelos sin migración: {diff}"
    assert head is not None and head.last_position == 0
