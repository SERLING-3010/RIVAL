import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.domain.roles import TeamRole, UserRole
from app.services import auth_service, join_service, membership_service, team_service
from app.services.inputs import CreateTeamInput, JoinRequestInput, TeamSearchInput
from tests.conftest import register_input


def new_user(ctx, email: str, role: UserRole = UserRole.PLAYER):
    return auth_service.register_user(ctx, register_input(email=email, role=role))


def team_input(name: str = "Los Halcones", as_coach: bool = False) -> CreateTeamInput:
    return CreateTeamInput(
        name=name, sport_code="FOOTBALL", modality_code="F7",
        city="Barranquilla", neighborhood="El Prado", as_coach=as_coach,
    )


def test_player_creates_team_as_captain_admin(ctx):
    user = new_user(ctx, "cap@rival.test")
    team = team_service.create_team(ctx, user, team_input())
    detail = team_service.team_detail(ctx, team.id)
    assert detail.admin_user_id == user.id
    assert detail.members[0].role == TeamRole.CAPTAIN


def test_coach_creates_team_as_coach(ctx):
    coach = new_user(ctx, "dt@rival.test", UserRole.COACH)
    team = team_service.create_team(ctx, coach, team_input(as_coach=True))
    assert team_service.team_detail(ctx, team.id).members[0].role == TeamRole.COACH


def test_player_cannot_create_as_coach(ctx):
    with pytest.raises(PermissionDeniedError):
        team_service.create_team(ctx, new_user(ctx, "p@rival.test"), team_input(as_coach=True))


def test_referee_cannot_create_team(ctx):
    referee = new_user(ctx, "ref@rival.test", UserRole.REFEREE)
    with pytest.raises(PermissionDeniedError):
        team_service.create_team(ctx, referee, team_input())


def test_unknown_modality_rejected(ctx):
    data = team_input()
    data.modality_code = "B3X3"
    with pytest.raises(DomainError) as error:
        team_service.create_team(ctx, new_user(ctx, "x@rival.test"), data)
    assert error.value.code == "UNKNOWN_MODALITY"


def test_search_filters_by_city_case_insensitive(ctx):
    team_service.create_team(ctx, new_user(ctx, "a@rival.test"), team_input("Halcones"))
    page = team_service.search_teams(ctx, TeamSearchInput(city="barranquilla", sport_code="FOOTBALL"))
    assert [t.name for t in page.items] == ["Halcones"]
    assert team_service.search_teams(ctx, TeamSearchInput(city="Cali")).items == []


def test_join_request_flow(ctx):
    captain = new_user(ctx, "cap@rival.test")
    player = new_user(ctx, "jug@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    request = join_service.request_join(ctx, player, team.id, JoinRequestInput())
    with pytest.raises(ConflictError) as error:
        join_service.request_join(ctx, player, team.id, JoinRequestInput())
    assert error.value.code == "REQUEST_ALREADY_PENDING"
    join_service.decide(ctx, captain, request.id, approve=True)
    roles = {m.user_id: m.role for m in team_service.team_detail(ctx, team.id).members}
    assert roles[player.id] == TeamRole.PLAYER


def test_only_admin_decides_requests(ctx):
    captain = new_user(ctx, "cap@rival.test")
    outsider = new_user(ctx, "otro@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    request = join_service.request_join(ctx, new_user(ctx, "jug@rival.test"), team.id, JoinRequestInput())
    with pytest.raises(PermissionDeniedError):
        join_service.decide(ctx, outsider, request.id, approve=True)
    with pytest.raises(PermissionDeniedError):
        join_service.list_requests(ctx, outsider, team.id)


def test_approved_coach_becomes_admin(ctx):
    captain = new_user(ctx, "cap@rival.test")
    coach = new_user(ctx, "dt@rival.test", UserRole.COACH)
    team = team_service.create_team(ctx, captain, team_input())
    request = join_service.request_join(ctx, coach, team.id, JoinRequestInput(desired_role=TeamRole.COACH))
    join_service.decide(ctx, captain, request.id, approve=True)
    assert team_service.team_detail(ctx, team.id).admin_user_id == coach.id


def test_member_cannot_request_again(ctx):
    captain = new_user(ctx, "cap@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    with pytest.raises(ConflictError):
        join_service.request_join(ctx, captain, team.id, JoinRequestInput())


def test_coach_leaving_without_captain_is_blocked_then_allowed(ctx):
    coach = new_user(ctx, "dt@rival.test", UserRole.COACH)
    player = new_user(ctx, "jug@rival.test")
    team = team_service.create_team(ctx, coach, team_input(as_coach=True))
    request = join_service.request_join(ctx, player, team.id, JoinRequestInput())
    join_service.decide(ctx, coach, request.id, approve=True)
    with pytest.raises(DomainError) as error:
        membership_service.leave_team(ctx, coach, team.id)
    assert error.value.code == "ADMIN_SUCCESSOR_REQUIRED"
    membership_service.set_captain(ctx, coach, team.id, player.id)
    membership_service.leave_team(ctx, coach, team.id)
    assert team_service.team_detail(ctx, team.id).admin_user_id == player.id


def test_last_member_leaving_archives_team(ctx):
    captain = new_user(ctx, "cap@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    membership_service.leave_team(ctx, captain, team.id)
    assert team_service.search_teams(ctx, TeamSearchInput()).items == []


def test_my_teams_lists_role_and_pending_count(ctx):
    captain = new_user(ctx, "cap@rival.test")
    team = team_service.create_team(ctx, captain, team_input())
    join_service.request_join(ctx, new_user(ctx, "jug@rival.test"), team.id, JoinRequestInput())
    mine = team_service.my_teams(ctx, captain)
    assert mine[0].is_admin is True
    assert mine[0].pending_requests == 1

