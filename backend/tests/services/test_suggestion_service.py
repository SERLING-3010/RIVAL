import pytest

from app.domain.errors import PermissionDeniedError
from app.services import block_service, contract_service, suggestion_service
from tests.services.contract_helpers import matched_scene
from tests.services.match_helpers import setup_city
from tests.services.test_team_service import new_user


def names(items):
    return [s.team.name for s in items]


def test_suggests_close_teams_with_reasons_and_never_exact_distance(ctx):
    city = setup_city(ctx)  # Bravos a ~1 km, Cóndores a ~4 km, Lejanos a ~22 km de Águilas
    owner, team = city["uno"]
    got = suggestion_service.rivals_for(ctx, owner, team.id)
    assert names(got) == ["Bravos", "Cóndores"]  # Lejanos no tiene un motivo fuerte
    assert got[0].reasons == ["Está a menos de 2 km", "No se han enfrentado en el último mes"]
    assert got[1].distance_band == "FROM_2_TO_5_KM"
    assert all("km" not in r or r.startswith("Está a") for s in got for r in s.reasons)


def test_blocked_and_recent_rivals_are_left_out(ctx):
    scene = matched_scene(ctx)  # Águilas vs Bravos pactado
    for o in (scene["host_owner"], scene["guest_owner"]):
        contract_service.sign(ctx, o, scene["contract_id"], version=1)
    _tres_owner, tres = scene["city"]["tres"]
    assert names(suggestion_service.rivals_for(ctx, scene["host_owner"], scene["host"].id)) == ["Cóndores"]
    block_service.block(ctx, scene["host_owner"], scene["host"].id, tres.id)
    assert suggestion_service.rivals_for(ctx, scene["host_owner"], scene["host"].id) == []


def test_only_members_ask_for_their_team(ctx):
    city = setup_city(ctx)
    with pytest.raises(PermissionDeniedError):
        suggestion_service.rivals_for(ctx, new_user(ctx, "otro@r.test"), city["uno"][1].id)
