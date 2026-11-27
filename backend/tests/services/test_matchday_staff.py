"""Permisos del capitán cuando hay DT (Sprint 21)."""

from datetime import timedelta

import pytest

from app.domain.errors import PermissionDeniedError
from app.domain.roles import UserRole
from app.persistence.models_teams import TeamMembership
from app.services import callup_service, contract_queries, contract_service, result_service, tactics_service
from tests.services.contract_helpers import matched_scene
from tests.services.manager_helpers import add_player
from tests.services.test_team_service import new_user


@pytest.fixture
def s(ctx):
    scene = matched_scene(ctx)  # quien creó Águilas es su capitán; le agregamos un DT
    coach = new_user(ctx, "dt.aguilas@r.test", UserRole.COACH)
    scene["host"].memberships.append(TeamMembership(user_id=coach.id, role="COACH", joined_at=ctx.clock.now()))
    ctx.db.flush()
    scene.update(coach=coach, captain=scene["host_owner"], player=add_player(ctx, scene["host"], "j@r.test"))
    return scene


def test_captain_runs_matchday_but_does_not_commit_the_team(ctx, s, clock):
    view = contract_queries.get_contract(ctx, s["captain"], s["contract_id"])
    assert (view.is_admin, view.is_staff) == (False, True)
    coach_view = contract_queries.get_contract(ctx, s["coach"], s["contract_id"])
    assert (coach_view.is_admin, coach_view.is_staff) == (True, True)
    callup_service.call_up(ctx, s["captain"], s["contract_id"], [s["player"].id])  # convocatoria: sí
    assert tactics_service.view(ctx, s["captain"], s["contract_id"]).can_edit  # alineación: sí
    with pytest.raises(PermissionDeniedError):  # firmar compromete al equipo: solo el DT
        contract_service.sign(ctx, s["captain"], s["contract_id"], version=1)
    contract_service.sign(ctx, s["coach"], s["contract_id"], version=1)
    contract_service.sign(ctx, s["guest_owner"], s["contract_id"], version=1)
    clock.advance(timedelta(days=2))
    result_service.report(ctx, s["captain"], s["contract_id"], 2, 1)  # resultado: sí
    result = result_service.report(ctx, s["guest_owner"], s["contract_id"], 2, 1)
    assert result.status == "CONFIRMED"


def test_plain_players_only_watch(ctx, s):
    view = contract_queries.get_contract(ctx, s["player"], s["contract_id"])
    assert (view.is_admin, view.is_staff) == (False, False)
    assert not tactics_service.view(ctx, s["player"], s["contract_id"]).can_edit
    with pytest.raises(PermissionDeniedError) as denied:
        callup_service.call_up(ctx, s["player"], s["contract_id"], [s["player"].id])
    assert denied.value.code == "STAFF_ONLY"
