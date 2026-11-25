import pytest

from app.domain.errors import PermissionDeniedError
from app.services import callup_service, squad_queries, tactics_service
from tests.services.contract_helpers import matched_scene
from tests.services.manager_helpers import add_player
from tests.services.test_team_service import new_user


@pytest.fixture
def s(ctx):
    scene = matched_scene(ctx)  # Águilas (F7) vs Bravos
    scene["players"] = [add_player(ctx, scene["host"], f"j{i}@r.test") for i in range(8)]
    return scene


def test_without_saved_lineup_suggests_one_by_media(ctx, s):
    view = squad_queries.squad(ctx, s["players"][0], s["host"].id)
    assert (view.suggested, view.formation, view.players_per_side) == (True, "2-3-1", 7)
    assert len(view.starters) == 7 and view.subs == []
    assert len(view.members) == 9 and all(m.media == 57 and m.tier == "BRONCE" for m in view.members)
    assert (view.media, view.wins, view.draws, view.losses, view.badges) == (57, 0, 0, 0, [])


def test_saved_lineup_of_the_next_match_is_shown(ctx, s):
    callup_service.call_up(ctx, s["host_owner"], s["contract_id"], [p.id for p in s["players"]])
    for p in s["players"]:
        callup_service.respond(ctx, p, s["contract_id"], going=True)
    starters = [(p.id, "Arquero" if i == 0 else "Campo") for i, p in enumerate(s["players"][:7])]
    tactics_service.save(ctx, s["host_owner"], s["contract_id"], "3-2-1", starters, [s["players"][7].id])
    view = squad_queries.squad(ctx, s["host_owner"], s["host"].id)
    assert (view.suggested, view.formation) == (False, "3-2-1")
    assert [(st.user_id, st.position) for st in view.starters] == starters
    assert view.subs == [s["players"][7].id]


def test_only_members_see_the_squad(ctx, s):
    with pytest.raises(PermissionDeniedError):
        squad_queries.squad(ctx, new_user(ctx, "fuera@r.test"), s["host"].id)
    with pytest.raises(PermissionDeniedError):  # ni el rival del partido
        squad_queries.squad(ctx, s["guest_owner"], s["host"].id)
