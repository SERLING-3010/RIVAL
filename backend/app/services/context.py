"""Dependencias que comparten los casos de uso de una petición."""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.orm import Session

from app.domain.launch_rules import ALL, Features
from app.domain.sports_catalog import SportCatalog
from app.services.clock import Clock


@dataclass
class ServiceContext:
    db: Session
    clock: Clock
    catalog: SportCatalog
    session_ttl: timedelta
    session_idle: timedelta
    features: Features = ALL  # Sprint 29: alcance del lanzamiento
