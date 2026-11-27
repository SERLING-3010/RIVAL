"""Enviador de notificaciones push (Sprint 24). Cada minuto junta los pendientes nuevos y los avisa.

Uso:  python -m app.tools.push_worker          (sigue corriendo; Ctrl+C para parar)
      python -m app.tools.push_worker --once   (una sola ronda; para una tarea programada)
Usa RIVAL_DATABASE_URL igual que la API. Primero se marcan los avisos en la base y se confirma;
después se llama a Expo, para no tener una llamada externa dentro de la transacción.
"""

import sys
import time
import urllib.error
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.sports_catalog import SportCatalog
from app.persistence.database import make_engine, make_session_factory, session_scope
from app.services import expo_push, push_service
from app.services.clock import SystemClock
from app.services.context import ServiceContext
from app.settings import Settings

INTERVAL_SECONDS = 60


def run_once(settings: Settings) -> int:
    factory = make_session_factory(make_engine(settings.database_url))
    catalog = SportCatalog.load(settings.catalog_path)

    def ctx_for(session: Session) -> ServiceContext:
        return ServiceContext(db=session, clock=SystemClock(), catalog=catalog,
                              session_ttl=settings.session_ttl, session_idle=settings.session_idle)

    outgoing: list[push_service.Outgoing] = []
    for session in session_scope(factory):
        outgoing = push_service.collect(ctx_for(session))
    if not outgoing:
        return 0
    try:
        dead = expo_push.send(outgoing)
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"[{datetime.now():%H:%M:%S}] No se pudo hablar con Expo: {error}", flush=True)
        return 0
    for session in session_scope(factory):
        push_service.forget_tokens(ctx_for(session), dead)
    print(f"[{datetime.now():%H:%M:%S}] Avisos enviados a {len(outgoing)} persona(s)", flush=True)
    return len(outgoing)


def main() -> None:
    settings = Settings()
    if "--once" in sys.argv:
        run_once(settings)
        return
    print("Enviador de avisos corriendo. Ctrl+C para parar.", flush=True)
    while True:
        run_once(settings)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
