from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.persistence.models_audit import AuditEvent
from app.persistence.models_teams import TeamMembership
from app.services import contract_queries, contract_service
from app.services.audit_service import verify_chain
from tests.services.contract_helpers import changed_terms, current_terms, matched_scene


@pytest.fixture
def s(ctx):
    return matched_scene(ctx)


def view(ctx, s, actor=None):
    return contract_queries.get_contract(ctx, actor or s["host_owner"], s["contract_id"])


def test_accepting_offer_creates_contract_from_offer(ctx, s):
    contract = view(ctx, s)
    assert (contract.status, contract.current.version, contract.signed) == ("NEGOTIATING", 1, None)
    assert contract.current.terms.kickoff_at == s["offer"].proposed_start
    assert contract.current.terms.place_note == "Cancha de arena"
    assert (contract.host.id, contract.guest.id, contract.my_side) == (s["host"].id, s["guest"].id, "HOST")


def test_both_must_sign_same_version(ctx, s):
    contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=1)
    assert view(ctx, s).status == "NEGOTIATING"
    with pytest.raises(ConflictError) as twice:
        contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=1)
    assert twice.value.code == "ALREADY_SIGNED"
    contract_service.sign(ctx, s["guest_owner"], s["contract_id"], version=1)
    contract = view(ctx, s)
    assert (contract.status, contract.signed.version, contract.current.signed_by) == ("SIGNED", 1, ["HOST", "GUEST"])


def test_proposal_counts_as_proposer_signature_and_resets_other(ctx, s):
    contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=1)
    terms = changed_terms(ctx, s["guest_owner"], s["contract_id"], duration_minutes=80)
    contract_service.propose(ctx, s["guest_owner"], s["contract_id"], base_version=1, terms=terms, note="Más tiempo")
    contract = view(ctx, s)
    assert (contract.current.version, contract.current.signed_by, contract.status) == (2, ["GUEST"], "NEGOTIATING")
    with pytest.raises(ConflictError) as stale:
        contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=1)
    assert stale.value.code == "CONTRACT_VERSION_CHANGED"
    contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=2)
    assert view(ctx, s).signed.terms.duration_minutes == 80


def test_amendment_after_signing_keeps_signed_version_until_accepted(ctx, s):
    for owner in (s["host_owner"], s["guest_owner"]):
        contract_service.sign(ctx, owner, s["contract_id"], version=1)
    terms = changed_terms(ctx, s["host_owner"], s["contract_id"], host_kit_color="Rojo")
    contract_service.propose(ctx, s["host_owner"], s["contract_id"], base_version=1, terms=terms)
    contract = view(ctx, s)
    assert (contract.status, contract.signed.version, contract.current.version) == ("NEGOTIATING", 1, 2)
    with pytest.raises(ConflictError):  # la versión 1 ya no es la que está en discusión
        contract_service.reject_amendment(ctx, s["host_owner"], s["contract_id"], version=1)
    member = s["city"]["tres"][0]  # un jugador del local que no administra no puede decidir
    s["host"].memberships.append(TeamMembership(user_id=member.id, role="PLAYER", joined_at=ctx.clock.now()))
    ctx.db.flush()
    with pytest.raises(PermissionDeniedError):
        contract_service.reject_amendment(ctx, member, s["contract_id"], version=2)
    contract_service.reject_amendment(ctx, s["guest_owner"], s["contract_id"], version=2)
    contract = view(ctx, s)
    assert (contract.status, contract.current.version, contract.signed.terms.host_kit_color) == ("SIGNED", 1, "Oscuro")
    assert [v.version for v in contract.versions] == [1, 2]


def test_invalid_or_unchanged_proposals_rejected(ctx, s):
    same = current_terms(ctx, s["host_owner"], s["contract_id"])
    with pytest.raises(DomainError) as unchanged:
        contract_service.propose(ctx, s["host_owner"], s["contract_id"], base_version=1, terms=same)
    assert unchanged.value.code == "NO_CHANGES"
    clash = changed_terms(ctx, s["host_owner"], s["contract_id"], guest_kit_color="oscuro")
    with pytest.raises(DomainError) as invalid:
        contract_service.propose(ctx, s["host_owner"], s["contract_id"], base_version=1, terms=clash)
    assert invalid.value.code == "KIT_COLORS_CLASH"


def test_outsiders_cannot_see_or_act(ctx, s):
    stranger, _ = s["city"]["tres"]
    with pytest.raises(NotFoundError):
        view(ctx, s, actor=stranger)
    with pytest.raises(NotFoundError):
        contract_service.sign(ctx, stranger, s["contract_id"], version=1)


def test_cancel_requires_reason_and_blocks_further_changes(ctx, s):
    with pytest.raises(DomainError) as short:
        contract_service.cancel(ctx, s["guest_owner"], s["contract_id"], reason="no")
    assert short.value.code == "CANCEL_REASON_REQUIRED"
    contract_service.cancel(ctx, s["guest_owner"], s["contract_id"], reason="Nos faltan jugadores")
    assert view(ctx, s).status == "CANCELLED"
    with pytest.raises(ConflictError):
        contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=1)


def test_cannot_sign_after_kickoff(ctx, s, clock):
    clock.advance(timedelta(hours=31))
    with pytest.raises(DomainError) as late:
        contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=1)
    assert late.value.code == "KICKOFF_IN_PAST"


def test_no_changes_or_cancel_after_kickoff_of_signed_version(ctx, s, clock):
    for owner in (s["host_owner"], s["guest_owner"]):
        contract_service.sign(ctx, owner, s["contract_id"], version=1)
    clock.advance(timedelta(hours=31))
    later = changed_terms(ctx, s["host_owner"], s["contract_id"], kickoff_at=clock.now() + timedelta(days=1))
    with pytest.raises(ConflictError) as started:
        contract_service.propose(ctx, s["host_owner"], s["contract_id"], base_version=1, terms=later)
    assert started.value.code == "MATCH_ALREADY_STARTED"
    with pytest.raises(ConflictError):
        contract_service.cancel(ctx, s["guest_owner"], s["contract_id"], reason="Ya no podemos")


def test_every_step_is_audited(ctx, s):
    contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=1)
    contract_service.sign(ctx, s["guest_owner"], s["contract_id"], version=1)
    actions = [e.action for e in ctx.db.query(AuditEvent).filter(AuditEvent.entity == "match_contract")]
    assert actions == ["CONTRACT_CREATED", "CONTRACT_SIGNED", "CONTRACT_SIGNED"]
    assert verify_chain(ctx.db)
