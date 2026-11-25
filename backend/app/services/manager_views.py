"""Vistas del modo manager (Sprint 7). Nunca incluyen correos ni datos personales."""

from dataclasses import dataclass
from datetime import datetime

from app.services.team_views import TeamSummaryView


@dataclass(frozen=True)
class PlayerStats:
    matches: int
    goals: int
    wins: int
    draws: int
    losses: int


@dataclass(frozen=True)
class FeatGoalView:
    label: str  # "10 goles", "Gol de chilena"…
    current: int
    target: int


@dataclass(frozen=True)
class SpecialCardView:
    code: str  # uno de special_cards.CODES
    min_media: int
    earned_at: datetime | None  # None mientras no la gana
    goals: list[FeatGoalView]


@dataclass(frozen=True)
class CardFaceView:
    """Lo que muestra la carta del jugador (Sprints 20 y 23); se calcula en `card_queries`."""

    media: int
    tier: str  # carta básica: BRONCE, PLATA, ORO u ORO_BRILLANTE
    next_tier: str | None
    media_to_next: int  # media que falta para la siguiente básica
    display_tier: str  # la que se dibuja: la especial más difícil que tiene, o su básica
    market_value: int  # monedas RIVAL virtuales; no se compran ni se venden
    specials: list[SpecialCardView]  # las quince, ganadas o no, con su avance
    hat_tricks: int
    check_ins: int  # partidos con check-in en la cancha (Sprint 22)
    recent: list[str]  # W, D o L, del más reciente al más antiguo
    badges: list[str]  # nombres de las insignias ganadas


@dataclass(frozen=True)
class PlayerCardView:
    user_id: int
    display_name: str
    position: str | None
    sports: list[str]
    teams: list[TeamSummaryView]
    matches: int
    goals: int
    wins: int
    draws: int
    losses: int
    rating_average: float | None  # promedio de valoraciones de compañeros (Sprint 10)
    rating_votes: int
    card: CardFaceView


@dataclass(frozen=True)
class MarketItemView:
    player_id: int
    display_name: str
    position: str | None
    team: TeamSummaryView
    matches: int
    goals: int


@dataclass(frozen=True)
class TransferOfferView:
    id: int
    player_id: int
    player_name: str
    from_team: TeamSummaryView
    to_team: TeamSummaryView
    amount: int
    status: str
    created_at: datetime


@dataclass(frozen=True)
class CoinEntryView:
    amount: int
    reason: str
    reference: str | None
    created_at: datetime


@dataclass(frozen=True)
class SquadMemberView:
    user_id: int
    display_name: str
    role: str
    position: str | None
    listed: bool
    matches: int
    goals: int


@dataclass(frozen=True)
class TeamManagerView:
    team: TeamSummaryView
    is_admin: bool
    balance: int
    level: int | None  # nivel Glicko-2 (Sprint 10)
    level_rd: int | None
    level_matches: int
    history: list[CoinEntryView]
    squad: list[SquadMemberView]
    offers_received: list[TransferOfferView]  # por jugadores de este equipo (solo para el administrador)
    offers_sent: list[TransferOfferView]  # de este equipo por jugadores de otros (solo para el administrador)
