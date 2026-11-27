"""Rutas del modo manager: ficha, plantilla con monedas, mercado de fichajes y planilla del partido."""

from dataclasses import asdict
from typing import Annotated, Literal

from fastapi import APIRouter, Query

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_manager import (
    LineupBody, ListingBody, MarketItemOut, PlayerCardOut, TeamManagerOut, TransferOfferBody, TransferOfferOut,
)
from app.persistence.models_identity import UserAccount
from app.services import lineup_service, manager_queries, transfer_listing_service, transfer_service
from app.services.context import ServiceContext

router = APIRouter(prefix="/api/v1")


def _manager(ctx: ServiceContext, user: UserAccount, team_id: int) -> TeamManagerOut:
    return TeamManagerOut.model_validate(asdict(manager_queries.team_manager(ctx, user, team_id)))


def _offer(ctx: ServiceContext, offer_id: int) -> TransferOfferOut:
    return TransferOfferOut.model_validate(asdict(manager_queries.offer_view(ctx, offer_id)))


@router.get("/players/{user_id}/card")
def player_card(user_id: int, ctx: CtxDep, user: UserDep) -> PlayerCardOut:
    return PlayerCardOut.model_validate(asdict(manager_queries.player_card(ctx, user, user_id)))


@router.get("/teams/{team_id}/manager")
def team_manager(team_id: int, ctx: CtxDep, user: UserDep) -> TeamManagerOut:
    return _manager(ctx, user, team_id)


@router.post("/teams/{team_id}/transfer-list")
def set_listed(team_id: int, body: ListingBody, ctx: CtxDep, user: UserDep) -> TeamManagerOut:
    transfer_listing_service.set_listed(ctx, user, team_id, body.user_id, body.listed)
    return _manager(ctx, user, team_id)


@router.get("/market")
def market(
    ctx: CtxDep,
    user: UserDep,
    sport: Annotated[str, Query(max_length=30)],
    city: Annotated[str | None, Query(max_length=60)] = None,
) -> list[MarketItemOut]:
    return [MarketItemOut.model_validate(asdict(v)) for v in manager_queries.market(ctx, user, sport, city)]


@router.post("/teams/{team_id}/transfer-offers", status_code=201)
def make_offer(team_id: int, body: TransferOfferBody, ctx: CtxDep, user: UserDep) -> TransferOfferOut:
    offer = transfer_service.make_offer(ctx, user, team_id, body.player_id, body.amount)
    return _offer(ctx, offer.id)


@router.get("/me/transfer-offers")
def my_offers(ctx: CtxDep, user: UserDep) -> list[TransferOfferOut]:
    return [TransferOfferOut.model_validate(asdict(v)) for v in manager_queries.my_offers(ctx, user)]


@router.post("/transfer-offers/{offer_id}/{decision}")
def decide(
    offer_id: int,
    decision: Literal["owner-accept", "owner-reject", "player-accept", "player-reject", "withdraw"],
    ctx: CtxDep,
    user: UserDep,
) -> TransferOfferOut:
    if decision.startswith("owner-"):
        transfer_service.decide_owner(ctx, user, offer_id, accept=decision == "owner-accept")
    elif decision.startswith("player-"):
        transfer_service.decide_player(ctx, user, offer_id, accept=decision == "player-accept")
    else:
        transfer_service.withdraw(ctx, user, offer_id)
    return _offer(ctx, offer_id)


@router.post("/contracts/{contract_id}/lineup")
def record_lineup(contract_id: int, body: LineupBody, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    lineup_service.record(ctx, user, contract_id, [(p.user_id, p.goals) for p in body.players],
                          {p.user_id: p.kinds for p in body.players if p.kinds})
    return {"contract_id": contract_id, "players": len(body.players)}
