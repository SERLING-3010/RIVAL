"""Vistas del contrato de partido (Sprint 3)."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.contract_rules import ContractTerms
from app.services.team_views import TeamSummaryView


@dataclass(frozen=True)
class VersionView:
    version: int
    terms: ContractTerms
    proposed_by_side: str | None  # None = versión inicial creada por el sistema desde la oferta
    note: str | None
    created_at: datetime
    signed_by: list[str]  # lados que firmaron esta versión: "HOST", "GUEST"


@dataclass(frozen=True)
class ContractView:
    id: int
    request_id: int
    host: TeamSummaryView
    guest: TeamSummaryView
    status: str
    my_side: str
    is_admin: bool
    current: VersionView
    signed: VersionView | None
    versions: list[VersionView]
    cancel_reason: str | None


@dataclass(frozen=True)
class ContractSummaryView:
    id: int
    host: TeamSummaryView
    guest: TeamSummaryView
    status: str
    kickoff_at: datetime
    my_side: str
    awaiting_my_signature: bool
