"""Entorno de Alembic para RIVAL (Sprint 9).

La URL sale de RIVAL_DATABASE_URL (la misma de la API), nunca de alembic.ini: ningún secreto en el código.
Uso:  python -m alembic upgrade head
"""

from logging.config import fileConfig

from alembic import context

from app.persistence.database import Base, load_models, make_engine
from app.settings import Settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

load_models()
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=Settings().database_url, target_metadata=target_metadata, literal_binds=True,
                      dialect_opts={"paramstyle": "named"}, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = make_engine(Settings().database_url)
    with engine.connect() as connection:
        # render_as_batch: SQLite no soporta ALTER TABLE completo; Alembic recrea la tabla.
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True,
                          compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
