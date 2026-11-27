from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.persistence.models_audit import AuditEvent
from app.persistence.models_teams import TeamMembership
from app.services import contract_queries, contract_service, result_service
from tests.services.contract_helpers import matched_scene


@pytest.fixture
def s(ctx, clock):
    scene = matched_scene(ctx)
    for owner in (scene["host_owner"], scene["guest_owner"]):
        contract_service.sign(ctx, owner, scene["contract_id"], version=1)
    clock.advance(timedelta(hours=31))  # la oferta proponía jugar 30 h después
    return scene


def result(ctx, s):
    return contract_queries.get_contract(ctx, s["host_owner"], s["contract_id"]).result


def test_matching_reports_confirm(ctx, s):
    result_service.report(ctx, s["host_owner"], s["contract_id"], 3, 1)
    pending = result(ctx, s)
    assert (pending.status, pending.host_score, [r.side for r in pending.reports]) == ("PENDING", None, ["HOST"])
    result_service.report(ctx, s["guest_owner"], s["contract_id"], 3, 1)
    confirmed = result(ctx, s)
    assert (confirmed.status, confirmed.host_score, confirmed.guest_score) == ("CONFIRMED", 3, 1)
    with pytest.raises(ConflictError) as locked:
        result_service.report(ctx, s["host_owner"], s["contract_id"], 4, 1)
    assert locked.value.code == "RESULT_ALREADY_CONFIRMED"


def test_mismatch_disputes_until_corrected(ctx, s):
    result_service.report(ctx, s["host_owner"], s["contract_id"], 2, 2)
    result_service.report(ctx, s["guest_owner"], s["contract_id"], 1, 2)
    assert result(ctx, s).status == "DISPUTED"
    result_service.report(ctx, s["guest_owner"], s["contract_id"], 2, 2)
    assert (result(ctx, s).status, result(ctx, s).host_score) == ("CONFIRMED", 2)
    actions = [e.action for e in ctx.db.query(AuditEvent).filter(AuditEvent.action.like("RESULT_%"))]
    assert actions == ["RESULT_REPORTED", "RESULT_DISPUTED", "RESULT_CONFIRMED"]


def test_cannot_report_before_kickoff_or_unsigned(ctx, clock):
    scene = matched_scene(ctx)
    with pytest.raises(ConflictError) as unsigned:
        result_service.report(ctx, scene["host_owner"], scene["contract_id"], 1, 0)
    assert unsigned.value.code == "CONTRACT_NOT_SIGNED"
    for owner in (scene["host_owner"], scene["guest_owner"]):
        contract_service.sign(ctx, owner, scene["contract_id"], version=1)
    with pytest.raises(DomainError) as early:
        result_service.report(ctx, scene["host_owner"], scene["contract_id"], 1, 0)
    assert early.value.code == "RESULT_TOO_EARLY"


def test_only_admins_of_the_two_teams(ctx, s):
    stranger, _ = s["city"]["tres"]
    with pytest.raises(NotFoundError):
        result_service.report(ctx, stranger, s["contract_id"], 1, 0)
    s["host"].memberships.append(TeamMembership(user_id=stranger.id, role="PLAYER", joined_at=ctx.clock.now()))
    ctx.db.flush()
    with pytest.raises(PermissionDeniedError):
        result_service.report(ctx, stranger, s["contract_id"], 1, 0)


def test_score_range(ctx, s):
    with pytest.raises(DomainError) as error:
        result_service.report(ctx, s["host_owner"], s["contract_id"], 1000, 0)
    assert error.value.code == "SCORE_OUT_OF_RANGE"


def test_summary_shows_score(ctx, s):
    for owner in (s["host_owner"], s["guest_owner"]):
        result_service.report(ctx, owner, s["contract_id"], 0, 0)
    item = contract_queries.team_contracts(ctx, s["guest_owner"], s["guest"].id)[0]
    assert (item.result_status, item.host_score, item.guest_score) == ("CONFIRMED", 0, 0)
