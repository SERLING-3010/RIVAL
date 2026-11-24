"""Rutas de búsquedas de partido (abiertas o retos) y ofertas."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import CtxDep, UserDep
from app.api.routes_scouting import SearchUser
from app.api.schemas_scouting import MatchRequestBody, MatchRequestOut, OfferBody, OfferOut
from app.domain.geo import DEFAULT_RADIUS_KM, SearchScope
from app.services import contract_queries, match_feed_service, match_offer_service, match_request_service
from app.services.match_request_service import to_view
from app.services.match_views import MatchRequestInput, OfferInput

router = APIRouter(prefix="/api/v1")


def _status(item: object) -> dict[str, object]:
    return {"id": getattr(item, "id"), "status": getattr(item, "status")}


@router.post("/teams/{team_id}/match-requests", status_code=201)
def create_request(team_id: int, body: MatchRequestBody, ctx: CtxDep, user: UserDep) -> MatchRequestOut:
    data = MatchRequestInput(**{**body.model_dump(), "scope": SearchScope(body.scope)})
    request = match_request_service.create_request(ctx, user, team_id, data)
    return MatchRequestOut.model_validate(asdict(to_view(ctx, request)))


@router.get("/teams/{team_id}/match-requests")
def team_requests(team_id: int, ctx: CtxDep, user: UserDep) -> list[MatchRequestOut]:
    return [MatchRequestOut.model_validate(asdict(v)) for v in match_request_service.team_requests(ctx, user, team_id)]


@router.get("/teams/{team_id}/match-feed")
def match_feed(
    team_id: int, ctx: CtxDep, user: SearchUser,
    scope: SearchScope = SearchScope.CITY,
    radius_km: Annotated[int, Query(ge=1, le=15)] = DEFAULT_RADIUS_KM,
) -> list[MatchRequestOut]:
    views = match_feed_service.open_requests_for(ctx, user, team_id, scope, radius_km)
    return [MatchRequestOut.model_validate(asdict(v)) for v in views]


@router.post("/match-requests/{request_id}/cancel")
def cancel_request(request_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    return _status(match_request_service.cancel_request(ctx, user, request_id))


@router.post("/teams/{team_id}/match-requests/{request_id}/offers", status_code=201)
def make_offer(team_id: int, request_id: int, body: OfferBody, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    offer = match_offer_service.make_offer(ctx, user, team_id, request_id, OfferInput(**body.model_dump()))
    return {**_status(offer), "version": offer.version}


@router.get("/match-requests/{request_id}/offers")
def list_offers(request_id: int, ctx: CtxDep, user: UserDep) -> list[OfferOut]:
    return [OfferOut.model_validate(asdict(v)) for v in match_offer_service.list_offers(ctx, user, request_id)]


@router.post("/offers/{offer_id}/accept")
def accept_offer(offer_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    offer = match_offer_service.decide(ctx, user, offer_id, accept=True)
    return {**_status(offer), "contract_id": contract_queries.contract_id_for_offer(ctx, offer.id)}


@router.post("/offers/{offer_id}/reject")
def reject_offer(offer_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    return _status(match_offer_service.decide(ctx, user, offer_id, accept=False))


@router.post("/offers/{offer_id}/withdraw")
def withdraw_offer(offer_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    return _status(match_offer_service.withdraw(ctx, user, offer_id))
