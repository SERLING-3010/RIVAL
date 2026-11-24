"""Configuración por variables de entorno. Ningún secreto vive en el código."""

import os
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

DEFAULT_CATALOG = Path(__file__).resolve().parent / "config" / "sports.json"


def _origins() -> list[str]:
    raw = os.getenv("RIVAL_CORS_ORIGINS", "http://localhost:8081")
    return [o.strip() for o in raw.split(",") if o.strip() and o.strip() != "*"]


@dataclass
class Settings:
    database_url: str = field(default_factory=lambda: os.getenv("RIVAL_DATABASE_URL", "sqlite:///./rival_dev.db"))
    cors_origins: list[str] = field(default_factory=_origins)
    session_ttl: timedelta = field(
        default_factory=lambda: timedelta(hours=int(os.getenv("RIVAL_SESSION_TTL_HOURS", "168")))
    )
    session_idle: timedelta = field(
        default_factory=lambda: timedelta(hours=int(os.getenv("RIVAL_SESSION_IDLE_HOURS", "72")))
    )
    catalog_path: Path = DEFAULT_CATALOG
    debug: bool = field(default_factory=lambda: os.getenv("RIVAL_DEBUG", "false").lower() == "true")
