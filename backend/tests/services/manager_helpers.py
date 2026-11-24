"""Ayudas de pruebas del modo manager [SIMULACIÓN]."""

from datetime import timedelta

from app.persistence.models_teams import TeamMembership
from app.services import contract_service, result_service
from tests.services.contract_helpers import matched_scene
from tests.services.test_team_service import new_user


def add_player(ctx, team, email, sports=("FOOTBALL",)):
    """Agrega un jugador raso (rol PLAYER) directamente a la plantilla."""
    user = new_user(ctx, email)
    team.memberships.append(TeamMembership(user_id=user.id, role="PLAYER", joined_at=ctx.clock.now()))
    ctx.db.flush()
    return user


def confirmed_match(ctx, clock, host_score=2, guest_score=1):
    """Águilas (local) contra Bravos, firmado, jugado y con resultado confirmado."""
    s = matched_scene(ctx)
    for owner in (s["host_owner"], s["guest_owner"]):
        contract_service.sign(ctx, owner, s["contract_id"], version=1)
    clock.advance(timedelta(hours=31))
    for owner in (s["host_owner"], s["guest_owner"]):
        result_service.report(ctx, owner, s["contract_id"], host_score, guest_score)
    return s
