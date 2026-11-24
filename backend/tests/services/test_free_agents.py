import pytest

from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.roles import TeamRole, UserRole
from app.services import free_agent_service, invitation_service, team_service
from app.services.inputs import TeamSearchInput
from tests.services.test_team_service import new_user, team_input


def test_player_marks_free_agent_and_appears_in_search(ctx):
    player = new_user(ctx, "libre@r.test")
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position="Arquero", note=None)
    scout = new_user(ctx, "dt@r.test", UserRole.COACH)
    page = free_agent_service.search(ctx, scout, sport_code="FOOTBALL", city="barranquilla")
    assert [(a.display_name, a.position, a.neighborhood) for a in page.items] == [("José Peña", "Arquero", "El Prado")]
    assert not hasattr(page.items[0], "email")


def test_inactive_profile_is_hidden(ctx):
    player = new_user(ctx, "libre@r.test")
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=False, position=None, note=None)
    assert free_agent_service.search(ctx, player, sport_code="FOOTBALL", city="Barranquilla").total == 0


def test_referee_cannot_be_free_agent(ctx):
    referee = new_user(ctx, "ref@r.test", UserRole.REFEREE)
    with pytest.raises(PermissionDeniedError):
        free_agent_service.set_free_agent(ctx, referee, "FOOTBALL", active=True, position=None, note=None)


def test_invitation_flow_requires_player_acceptance(ctx):
    captain = new_user(ctx, "cap@r.test")
    player = new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    invitation = invitation_service.invite(ctx, captain, team.id, player.id, "¿Juegas el sábado?")
    with pytest.raises(ConflictError):
        invitation_service.invite(ctx, captain, team.id, player.id, None)
    assert [i.team.name for i in invitation_service.my_invitations(ctx, player)] == ["Los Halcones"]
    with pytest.raises(NotFoundError):
        invitation_service.respond(ctx, captain, invitation.id, accept=True)
    invitation_service.respond(ctx, player, invitation.id, accept=True)
    roles = {m.user_id: m.role for m in team_service.team_detail(ctx, team.id).members}
    assert roles[player.id] == TeamRole.PLAYER
    assert free_agent_service.search(ctx, captain, sport_code="FOOTBALL", city="Barranquilla").total == 0


def test_cannot_invite_someone_not_free_agent(ctx):
    captain = new_user(ctx, "cap@r.test")
    other = new_user(ctx, "otro@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    with pytest.raises(ConflictError) as error:
        invitation_service.invite(ctx, captain, team.id, other.id, None)
    assert error.value.code == "NOT_A_FREE_AGENT"


def test_only_admin_invites(ctx):
    captain = new_user(ctx, "cap@r.test")
    outsider = new_user(ctx, "x@r.test")
    player = new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    with pytest.raises(PermissionDeniedError):
        invitation_service.invite(ctx, outsider, team.id, player.id, None)


def test_invitation_is_not_listed_as_join_request(ctx):
    from app.services import join_service

    captain = new_user(ctx, "cap@r.test")
    player = new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    invitation_service.invite(ctx, captain, team.id, player.id, None)
    assert join_service.list_requests(ctx, captain, team.id) == []
    assert team_service.search_teams(ctx, TeamSearchInput()).total == 1
