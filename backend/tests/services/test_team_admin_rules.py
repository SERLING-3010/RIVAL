"""Reglas de administración y protecciones de la plantilla (revisión independiente del Sprint 1)."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.errors import PermissionDeniedError
from app.domain.roles import TeamRole, UserRole
from app.persistence.models_audit import AuditEvent
from app.persistence.models_teams import TeamMembership
from app.services import join_service, membership_service, team_service
from app.services.inputs import JoinRequestInput, TeamSearchInput
from tests.services.test_team_service import new_user, team_input


def test_approving_coach_records_admin_change(ctx):
    captain = new_user(ctx, "cap@rival.test")
    coach = new_user(ctx, "dt@rival.test", UserRole.COACH)
    team = team_service.create_team(ctx, captain, team_input())
    request = join_service.request_join(ctx, coach, team.id, JoinRequestInput(desired_role=TeamRole.COACH))
    join_service.decide(ctx, captain, request.id, approve=True)
    actions = [e.action for e in ctx.db.scalars(select(AuditEvent).order_by(AuditEvent.chain_position))]
    assert actions[-1] == "TEAM_ADMIN_CHANGED"


def test_captain_admin_naming_new_captain_hands_over_admin(ctx):
    captain = new_user(ctx, "cap@rival.test")
    player = new_user(ctx, "jug@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    join_service.decide(ctx, captain, join_service.request_join(ctx, player, team.id, JoinRequestInput()).id, True)
    membership_service.set_captain(ctx, captain, team.id, player.id)
    detail = team_service.team_detail(ctx, team.id)
    assert detail.admin_user_id == player.id
    assert [m.role for m in detail.members].count(TeamRole.CAPTAIN) == 1


def test_database_rejects_second_captain(ctx):
    captain = new_user(ctx, "cap@rival.test")
    other = new_user(ctx, "otro@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    ctx.db.add(TeamMembership(team_id=team.id, user_id=other.id, role="CAPTAIN", joined_at=ctx.clock.now()))
    with pytest.raises(IntegrityError):
        ctx.db.flush()


def test_referee_cannot_request_to_join(ctx):
    captain = new_user(ctx, "cap@rival.test")
    referee = new_user(ctx, "ref@rival.test", UserRole.REFEREE)
    team = team_service.create_team(ctx, captain, team_input())
    with pytest.raises(PermissionDeniedError) as error:
        join_service.request_join(ctx, referee, team.id, JoinRequestInput())
    assert error.value.code == "ROLE_CANNOT_JOIN_TEAM"


def test_search_treats_percent_literally(ctx):
    team_service.create_team(ctx, new_user(ctx, "a@rival.test"), team_input("Halcones"))
    assert team_service.search_teams(ctx, TeamSearchInput(query="%")).items == []
