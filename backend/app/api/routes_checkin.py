"""Rutas del check-in en la cancha y de la ubicación del establecimiento (Sprint 15).

Las coordenadas del check-in solo viven en esta petición: no se guardan ni se registran.
"""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import AwareDatetime, BaseModel, Field

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel
from app.services import checkin_service, venue_service

router = APIRouter(prefix="/api/v1")


class PositionBody(StrictModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class CheckInItemOut(BaseModel):
    user_id: int
    display_name: str
    checked_in_at: AwareDatetime


class CheckInBoardOut(BaseModel):
    contract_id: int
    unavailable: str | None
    venue_name: str | None
    opens_at: AwareDatetime
    closes_at: AwareDatetime
    window_open: bool
    me_checked_in: bool
    items: list[CheckInItemOut]


@router.get("/contracts/{contract_id}/check-ins")
def check_in_board(contract_id: int, ctx: CtxDep, user: UserDep) -> CheckInBoardOut:
    return CheckInBoardOut.model_validate(asdict(checkin_service.board(ctx, user, contract_id)))


@router.post("/contracts/{contract_id}/check-ins")
def check_in(contract_id: int, body: PositionBody, ctx: CtxDep, user: UserDep) -> CheckInBoardOut:
    checkin_service.check_in(ctx, user, contract_id, body.latitude, body.longitude)
    return check_in_board(contract_id, ctx, user)


@router.post("/venues/{venue_id}/location")
def set_venue_location(venue_id: int, body: PositionBody, ctx: CtxDep, user: UserDep) -> dict[str, bool]:
    venue_service.set_location(ctx, user, venue_id, body.latitude, body.longitude)
    return {"has_location": True}
