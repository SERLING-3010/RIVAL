"""Entradas y vistas de solicitudes de partido y ofertas."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.geo import DistanceBand, SearchScope
from app.domain.match_rules import PlaceKind, RefereeMode
from app.services.team_views import TeamSummaryView


@dataclass
class MatchRequestInput:
    window_start: datetime
    window_end: datetime
    scope: SearchScope
    referee_mode: RefereeMode
    place_kind: PlaceKind
    radius_km: int | None = None
    target_team_id: int | None = None
    place_note: str | None = None
    message: str | None = None


@dataclass
class OfferInput:
    proposed_start: datetime
    referee_mode: RefereeMode
    place_kind: PlaceKind
    place_note: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class MatchRequestView:
    id: int
    team: TeamSummaryView
    target_team_id: int | None
    scope: str
    radius_km: int | None
    window_start: datetime
    window_end: datetime
    referee_mode: str
    place_kind: str
    place_note: str | None
    message: str | None
    status: str
    distance_band: DistanceBand | None
    pending_offers: int
    accepted_offer_id: int | None


@dataclass(frozen=True)
class OfferView:
    id: int
    request_id: int
    team: TeamSummaryView
    version: int
    proposed_start: datetime
    referee_mode: str
    place_kind: str
    place_note: str | None
    message: str | None
    status: str
