"""Concurrencia real de los Sprints 3 a 8: solo corre contra PostgreSQL (RIVAL_TEST_DATABASE_URL).

Cada prueba lanza dos acciones a la vez en sesiones distintas y comprueba que los bloqueos
FOR UPDATE y los índices únicos dejan el sistema en un estado válido.
"""

from datetime import timedelta

import pytest
from sqlalchemy import func, select

from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import CoinEntry
from app.persistence.models_venues import Booking
from app.services import audit_service, booking_service, contract_service, health_service, result_service
from tests.conftest import TEST_DATABASE_URL
from tests.services.contract_helpers import changed_terms, matched_scene
from tests.services.test_concurrency_pg import factory, make_ctx, race  # noqa: F401  (fixture reutilizada)
from tests.services.venue_helpers import accepted_contract, sign_at_venue, signed_venue_match, slot_around
from tests.services.venue_helpers import venue_with_court

pytestmark = pytest.mark.skipif(TEST_DATABASE_URL.startswith("sqlite"), reason="requiere PostgreSQL")


def user(ctx, user_id):
    return ctx.db.get(UserAccount, user_id)


def test_both_admins_sign_at_once_contract_ends_signed(factory, clock):  # noqa: F811
    with factory() as session:
        s = matched_scene(make_ctx(session, clock))
        session.commit()
        ids = (s["host_owner"].id, s["guest_owner"].id, s["contract_id"])
    sign = [lambda ctx, u=u: contract_service.sign(ctx, user(ctx, u), ids[2], version=1) for u in ids[:2]]
    assert race(factory, clock, sign) == ["OK", "OK"]
    with factory() as session:
        assert session.get(MatchContract, ids[2]).status == "SIGNED"
        assert health_service.run_checks(make_ctx(session, clock)) == []


def test_sign_and_propose_at_once_never_sign_a_replaced_version(factory, clock):  # noqa: F811
    with factory() as session:
        ctx = make_ctx(session, clock)
        s = matched_scene(ctx)
        terms = changed_terms(ctx, s["guest_owner"], s["contract_id"], duration_minutes=90)
        contract_service.sign(ctx, s["guest_owner"], s["contract_id"], version=1)
        session.commit()
        ids = (s["host_owner"].id, s["guest_owner"].id, s["contract_id"])
    sign = lambda ctx: contract_service.sign(ctx, user(ctx, ids[0]), ids[2], version=1)  # noqa: E731
    propose = lambda ctx: contract_service.propose(ctx, user(ctx, ids[1]), ids[2], 1, terms)  # noqa: E731
    outcomes = race(factory, clock, [sign, propose])
    assert outcomes.count("OK") >= 1 and set(outcomes) - {"OK"} <= {"CONTRACT_VERSION_CHANGED"}
    with factory() as session:
        assert health_service.run_checks(make_ctx(session, clock)) == []
        assert audit_service.verify_chain(session) is True


def test_two_bookings_confirmed_at_once_only_one_wins(factory, clock):  # noqa: F811
    with factory() as session:
        ctx = make_ctx(session, clock)
        s = signed_venue_match(ctx)
        owner, _venue, court = venue_with_court(ctx)
        slot = slot_around(ctx, owner, court, s["kickoff"])
        tres, lejos = s["city"]["tres"], s["city"]["lejos"]
        other = accepted_contract(ctx, tres, lejos)
        sign_at_venue(ctx, tres[0], lejos[0], other)
        first = booking_service.request(ctx, s["guest_owner"], s["contract_id"], slot.id)
        second = booking_service.request(ctx, tres[0], other, slot.id)
        session.commit()
        ids = (owner.id, first.id, second.id, slot.id)
    confirm = [lambda ctx, b=b: booking_service.decide(ctx, user(ctx, ids[0]), b, confirm=True) for b in ids[1:3]]
    outcomes = race(factory, clock, confirm)
    assert outcomes.count("OK") == 1 and set(outcomes) - {"OK"} <= {"BOOKING_NOT_PENDING", "SLOT_TAKEN"}
    with factory() as session:
        confirmed = session.scalar(select(func.count()).select_from(Booking).where(
            Booking.slot_id == ids[3], Booking.status == "CONFIRMED"))
        assert confirmed == 1


def test_last_report_and_correction_at_once_pay_rewards_once(factory, clock):  # noqa: F811
    with factory() as session:
        ctx = make_ctx(session, clock)
        s = matched_scene(ctx)
        for owner in (s["host_owner"], s["guest_owner"]):
            contract_service.sign(ctx, owner, s["contract_id"], version=1)
        clock.advance(timedelta(hours=31))
        result_service.report(ctx, s["host_owner"], s["contract_id"], 2, 1)
        session.commit()
        ids = (s["host_owner"].id, s["guest_owner"].id, s["contract_id"], s["host"].id)
    guest_confirms = lambda ctx: result_service.report(ctx, user(ctx, ids[1]), ids[2], 2, 1)  # noqa: E731
    host_corrects = lambda ctx: result_service.report(ctx, user(ctx, ids[0]), ids[2], 2, 1)  # noqa: E731
    race(factory, clock, [guest_confirms, host_corrects])
    with factory() as session:
        rewards = session.scalar(select(func.count()).select_from(CoinEntry).where(
            CoinEntry.team_id == ids[3], CoinEntry.reason == "MATCH_REWARD"))
        assert rewards == 1
        assert audit_service.verify_chain(session) is True
