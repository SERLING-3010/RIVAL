"""Esquemas del modo manager (Sprint 7)."""

from pydantic import AwareDatetime, BaseModel, Field

from app.api.schemas_auth import StrictModel
from app.api.schemas_teams import TeamSummaryOut


class ListingBody(StrictModel):
    user_id: int
    listed: bool


class TransferOfferBody(StrictModel):
    player_id: int
    amount: int = Field(ge=1, le=1_000_000)


class LineupEntry(StrictModel):
    user_id: int
    goals: int = Field(ge=0, le=999)


class LineupBody(StrictModel):
    players: list[LineupEntry] = Field(min_length=1, max_length=40)


class CardFaceOut(BaseModel):
    media: int
    tier: str
    next_tier: str | None
    matches_to_next: int
    hat_tricks: int
    recent: list[str]
    badges: list[str]


class PlayerCardOut(BaseModel):
    user_id: int
    display_name: str
    position: str | None
    sports: list[str]
    teams: list[TeamSummaryOut]
    matches: int
    goals: int
    wins: int
    draws: int
    losses: int
    rating_average: float | None
    rating_votes: int
    card: CardFaceOut


class MarketItemOut(BaseModel):
    player_id: int
    display_name: str
    position: str | None
    team: TeamSummaryOut
    matches: int
    goals: int


class TransferOfferOut(BaseModel):
    id: int
    player_id: int
    player_name: str
    from_team: TeamSummaryOut
    to_team: TeamSummaryOut
    amount: int
    status: str
    created_at: AwareDatetime


class CoinEntryOut(BaseModel):
    amount: int
    reason: str
    reference: str | None
    created_at: AwareDatetime


class SquadMemberOut(BaseModel):
    user_id: int
    display_name: str
    role: str
    position: str | None
    listed: bool
    matches: int
    goals: int


class TeamManagerOut(BaseModel):
    team: TeamSummaryOut
    is_admin: bool
    balance: int
    level: int | None
    level_rd: int | None
    level_matches: int
    history: list[CoinEntryOut]
    squad: list[SquadMemberOut]
    offers_received: list[TransferOfferOut]
    offers_sent: list[TransferOfferOut]
