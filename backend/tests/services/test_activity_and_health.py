from datetime import timedelta

import pytest

from app.domain.errors import NotFoundError, PermissionDeniedError
from app.persistence.models_audit import AuditEvent
from app.persistence.models_contracts import MatchContractSignature
from app.persistence.models_teams import TeamMembership
from app.services import activity_service, contract_service, health_service
from tests.services.contract_helpers import matched_scene


@pytest.fixture
def s(ctx):
    return matched_scene(ctx)


def test_contract_activity_shows_who_did_what(ctx, s):
    contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=1)
    items = activity_service.contract_activity(ctx, s["guest_owner"], s["contract_id"])
    actions = [i.action for i in items]
    assert actions[:2] == ["CONTRACT_SIGNED", "CONTRACT_CREATED"]  # lo más reciente primero
    assert {"MATCH_OFFER_ACCEPTED", "MATCH_OFFER_MADE", "MATCH_REQUEST_CREATED"} <= set(actions)
    signed = items[0]
    assert (signed.actor_name, signed.after["version"]) == ("José Peña", 1)
    with pytest.raises(NotFoundError):
        activity_service.contract_activity(ctx, s["city"]["tres"][0], s["contract_id"])


def test_team_activity_only_for_members_and_without_private_data(ctx, s):
    items = activity_service.team_activity(ctx, s["host_owner"], s["host"].id)
    actions = {i.action for i in items}
    assert {"TEAM_CREATED", "MATCH_REQUEST_CREATED", "CONTRACT_CREATED"} <= actions
    assert "USER_REGISTERED" not in actions and "USER_LOGGED_IN" not in actions
    assert all("@" not in str(i.after) for i in items)
    with pytest.raises(PermissionDeniedError):
        activity_service.team_activity(ctx, s["guest_owner"], s["host"].id)


def test_health_is_clean_for_a_normal_flow(ctx, s):
    assert health_service.run_checks(ctx) == []


def test_health_detects_overdue_result_and_tampered_signature(ctx, s, clock):
    for owner in (s["host_owner"], s["guest_owner"]):
        contract_service.sign(ctx, owner, s["contract_id"], version=1)
    clock.advance(timedelta(hours=30 + 49))
    assert [f.code for f in health_service.run_checks(ctx)] == ["RESULT_OVERDUE"]
    ctx.db.query(MatchContractSignature).filter(MatchContractSignature.team_id == s["guest"].id).delete()
    codes = {f.code: f.severity for f in health_service.run_checks(ctx)}
    assert codes["SIGNED_WITHOUT_TWO_SIGNATURES"] == "S0"


def test_health_detects_team_without_admin_and_broken_chain(ctx, s):
    ctx.db.query(TeamMembership).filter(TeamMembership.team_id == s["host"].id).delete()
    ctx.db.query(AuditEvent).filter(AuditEvent.chain_position == 1).update({"action": "EDITADO"})
    ctx.db.flush()
    ctx.db.expire_all()
    codes = {f.code: f.severity for f in health_service.run_checks(ctx)}
    assert codes == {"TEAM_WITHOUT_ADMIN": "S1", "AUDIT_CHAIN_BROKEN": "S0"}
