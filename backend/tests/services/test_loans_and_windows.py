from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.services import (
    callup_service, contract_service, league_enrollment_service as enroll, league_service, lineup_service,
    loan_queries, loan_service, manager_queries, result_service, transfer_listing_service, transfer_service,
    transfer_window_service,
)
from app.services.league_views import LeagueInput
from tests.services.contract_helpers import matched_scene
from tests.services.manager_helpers import add_player


@pytest.fixture
def s(ctx):
    scene = matched_scene(ctx)  # Águilas (local) vs Bravos; el préstamo viene de Cóndores
    lender_owner, lender = scene["city"]["tres"]
    scene.update(lender_owner=lender_owner, lender=lender, player=add_player(ctx, lender, "prestado@r.test"))
    return scene


def loan_for(ctx, s):
    return loan_service.request(ctx, s["host_owner"], s["contract_id"], s["player"].id, s["lender"].id)


def test_loan_needs_owner_then_player_and_enables_callup_and_lineup(ctx, s, clock):
    loan = loan_for(ctx, s)
    with pytest.raises(PermissionDeniedError):  # el jugador no decide antes que su DT
        loan_service.decide_player(ctx, s["player"], loan.id, accept=True)
    with pytest.raises(DomainError):  # todavía no se puede convocar
        callup_service.call_up(ctx, s["host_owner"], s["contract_id"], [s["player"].id])
    loan_service.decide_owner(ctx, s["lender_owner"], loan.id, accept=True)
    assert [l.id for l in loan_queries.awaiting_me(ctx, s["player"])] == [loan.id]
    loan_service.decide_player(ctx, s["player"], loan.id, accept=True)
    callup_service.call_up(ctx, s["host_owner"], s["contract_id"], [s["player"].id])
    assert [(l.player_name, l.status) for l in loan_queries.for_contract(ctx, s["host_owner"], s["contract_id"])] == [
        ("José Peña", "ACTIVE")]
    for owner in (s["host_owner"], s["guest_owner"]):
        contract_service.sign(ctx, owner, s["contract_id"], version=1)
    clock.advance(timedelta(hours=31))
    for owner in (s["host_owner"], s["guest_owner"]):
        result_service.report(ctx, owner, s["contract_id"], 1, 0)
    lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(s["player"].id, 1)])
    card = manager_queries.player_card(ctx, s["host_owner"], s["player"].id)
    assert (card.matches, card.goals, card.wins, [t.name for t in card.teams]) == (1, 1, 1, ["Cóndores"])


def test_loan_rules(ctx, s):
    with pytest.raises(DomainError):  # no al rival del mismo partido
        loan_service.request(ctx, s["host_owner"], s["contract_id"], s["guest_owner"].id, s["guest"].id)
    with pytest.raises(DomainError):  # no al capitán/DT del equipo dueño
        loan_service.request(ctx, s["host_owner"], s["contract_id"], s["lender_owner"].id, s["lender"].id)
    loan = loan_for(ctx, s)
    with pytest.raises(ConflictError):
        loan_for(ctx, s)
    with pytest.raises(PermissionDeniedError):  # un tercero no cancela
        loan_service.cancel(ctx, s["guest_owner"], loan.id)
    loan_service.cancel(ctx, s["player"], loan.id)
    loan_for(ctx, s)  # cancelado, se puede volver a pedir


def test_transfer_window_blocks_offers_and_completion(ctx, s, clock):
    seller_owner, seller = s["city"]["uno"]
    buyer_owner, buyer = s["city"]["dos"]
    player = add_player(ctx, seller, "fichaje@r.test")
    league = league_service.create_league(ctx, seller_owner, LeagueInput(
        name="Liga del Prado", sport_code="FOOTBALL", modality_code="F7", city="Ciudad Prueba", season="2026-2"))
    entry = enroll.request_team(ctx, seller_owner, league.id, seller.id)
    enroll.decide(ctx, seller_owner, "team", entry.id, approve=True)
    transfer_listing_service.set_listed(ctx, seller_owner, seller.id, player.id, listed=True)
    offer = transfer_service.make_offer(ctx, buyer_owner, buyer.id, player.id, 100)  # sin ventana: abierto
    transfer_service.decide_owner(ctx, seller_owner, offer.id, accept=True)
    now = ctx.clock.now()
    with pytest.raises(PermissionDeniedError):
        transfer_window_service.set_window(ctx, buyer_owner, league.id, now, now + timedelta(days=1))
    transfer_window_service.set_window(ctx, seller_owner, league.id, now + timedelta(days=3), now + timedelta(days=10))
    with pytest.raises(ConflictError) as closed:
        transfer_service.decide_player(ctx, player, offer.id, accept=True)
    assert closed.value.code == "TRANSFER_WINDOW_CLOSED"
    clock.advance(timedelta(days=4))
    transfer_service.decide_player(ctx, player, offer.id, accept=True)  # ventana abierta
    assert offer.status == "COMPLETED"
