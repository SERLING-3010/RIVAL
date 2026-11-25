from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.persistence.models_audit import AuditEvent
from app.services import callup_service, tactics_service
from tests.services.contract_helpers import matched_scene
from tests.services.manager_helpers import add_player
from tests.services.test_team_service import new_user


@pytest.fixture
def s(ctx):
    scene = matched_scene(ctx)  # Águilas (local, F7) vs Bravos
    players = [add_player(ctx, scene["host"], f"j{i}@r.test") for i in range(8)]
    callup_service.call_up(ctx, scene["host_owner"], scene["contract_id"], [p.id for p in players])
    for p in players:
        callup_service.respond(ctx, p, scene["contract_id"], going=True)
    scene["players"] = players
    return scene


def lineup(players):
    positions = ["Arquero", "Defensa", "Defensa", "Volante", "Volante", "Volante", "Delantero"]
    return [(p.id, pos) for p, pos in zip(players[:7], positions, strict=True)], [players[7].id]


def test_admin_saves_and_only_own_team_sees_it(ctx, s):
    starters, subs = lineup(s["players"])
    saved = tactics_service.save(ctx, s["host_owner"], s["contract_id"], "2-3-1", starters, subs)
    assert (saved.formation, len(saved.starters), len(saved.subs), saved.eligible) == ("2-3-1", 7, 1, [])
    mine = tactics_service.view(ctx, s["players"][3], s["contract_id"])
    assert mine.starters[0].position == "Arquero" and not mine.can_edit
    rival = tactics_service.view(ctx, s["guest_owner"], s["contract_id"])
    assert (rival.team_id, rival.formation, rival.starters) == (s["guest"].id, None, [])  # el rival no la ve
    with pytest.raises(NotFoundError):
        tactics_service.view(ctx, new_user(ctx, "curioso@r.test"), s["contract_id"])
    event = ctx.db.query(AuditEvent).filter(AuditEvent.action == "TACTICS_SET").one()
    assert "2-3-1" not in (event.after_json or "")  # la actividad la ven los dos equipos


def test_rules_and_permissions(ctx, s, clock):
    starters, subs = lineup(s["players"])
    with pytest.raises(PermissionDeniedError):
        tactics_service.save(ctx, s["players"][0], s["contract_id"], None, starters, subs)
    with pytest.raises(DomainError):
        tactics_service.save(ctx, s["host_owner"], s["contract_id"], "3-3-1", starters, subs)
    outsider = new_user(ctx, "nofue@r.test")
    with pytest.raises(DomainError):
        tactics_service.save(ctx, s["host_owner"], s["contract_id"], None, starters[:6] + [(outsider.id, "X")], [])
    clock.advance(timedelta(days=3))  # ya empezó
    with pytest.raises(ConflictError):
        tactics_service.save(ctx, s["host_owner"], s["contract_id"], None, starters, subs)


def test_player_who_backs_out_is_flagged(ctx, s):
    starters, subs = lineup(s["players"])
    tactics_service.save(ctx, s["host_owner"], s["contract_id"], None, starters, subs)
    callup_service.respond(ctx, s["players"][6], s["contract_id"], going=False)
    view = tactics_service.view(ctx, s["host_owner"], s["contract_id"])
    assert [p.still_going for p in view.starters] == [True] * 6 + [False]
