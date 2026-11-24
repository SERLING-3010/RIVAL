"""PostgreSQL 16 local para desarrollo, sin instalar PostgreSQL ni Docker (Sprint 9).

Requiere:  pip install -r requirements-pg-local.txt
Uso:       python dev_tools/local_pg.py
Imprime la URL para RIVAL_TEST_DATABASE_URL. Los datos quedan en backend/.pgdata (fuera de git).
"""

from pathlib import Path

import pgserver

DATA = Path(__file__).resolve().parents[1] / ".pgdata"


def main() -> None:
    server = pgserver.get_server(DATA, cleanup_mode=None)  # sigue corriendo al terminar el script
    if "rival_test" not in server.psql("select datname from pg_database;"):
        server.psql("create database rival_test;")
    uri = server.get_uri().replace("postgresql://", "postgresql+psycopg://").rsplit("/", 1)[0]
    print(f"{uri}/rival_test")


if __name__ == "__main__":
    main()
