import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.services import coin_service, health_service, manager_queries, transfer_listing_service, transfer_service
from app.services.team_service import team_detail
from tests.services.manager_helpers import add_player
from tests.services.test_rival_service import make_team


@pytest.fixture
def s(ctx):
    seller_owner, seller = make_team(ctx, "vende@r.test", "Águilas", "Barrio Uno")
    buyer_owner, buyer = make_team(ctx, "compra@r.test", "Bravos", "Barrio Dos")
    player = add_player(ctx, seller, "estrella@r.test")
    return {"seller_owner": seller_owner, "seller": seller, "buyer_owner": buyer_owner, "buyer": buyer,
            "player": player}


def members(ctx, team):
    return sorted(m.user_id for m in team_detail(ctx, team.id).members)


def test_full_transfer_needs_owner_and_player(ctx, s):
    transfer_listing_service.set_listed(ctx, s["seller_owner"], s["seller"].id, s["player"].id, listed=True)
    market = manager_queries.market(ctx, s["buyer_owner"], "FOOTBALL", "ciudad prueba")
    assert [(m.player_id, m.team.name) for m in market] == [(s["player"].id, "Águilas")]
    offer = transfer_service.make_offer(ctx, s["buyer_owner"], s["buyer"].id, s["player"].id, 300)
    with pytest.raises(PermissionDeniedError):  # el jugador no decide antes que su DT
        transfer_service.decide_player(ctx, s["player"], offer.id, accept=True)
    transfer_service.decide_owner(ctx, s["seller_owner"], offer.id, accept=True)
    assert offer.status == "PENDING_PLAYER" and s["player"].id in members(ctx, s["seller"])
    with pytest.raises(PermissionDeniedError):  # nadie acepta por el jugador
        transfer_service.decide_player(ctx, s["seller_owner"], offer.id, accept=True)
    transfer_service.decide_player(ctx, s["player"], offer.id, accept=True)
    assert offer.status == "COMPLETED"
    assert s["player"].id in members(ctx, s["buyer"]) and s["player"].id not in members(ctx, s["seller"])
    assert (coin_service.balance(ctx, s["buyer"].id), coin_service.balance(ctx, s["seller"].id)) == (700, 1300)
    assert manager_queries.market(ctx, s["buyer_owner"], "FOOTBALL", None) == []  # sale del mercado
    assert health_service.run_checks(ctx) == []


def test_player_can_refuse_and_nothing_moves(ctx, s):
    transfer_listing_service.set_listed(ctx, s["seller_owner"], s["seller"].id, s["player"].id, listed=True)
    offer = transfer_service.make_offer(ctx, s["buyer_owner"], s["buyer"].id, s["player"].id, 300)
    transfer_service.decide_owner(ctx, s["seller_owner"], offer.id, accept=True)
    transfer_service.decide_player(ctx, s["player"], offer.id, accept=False)
    assert offer.status == "REJECTED" and s["player"].id in members(ctx, s["seller"])
    assert coin_service.balance(ctx, s["buyer"].id) == 1000


def test_offer_rules(ctx, s):
    with pytest.raises(ConflictError) as unlisted:
        transfer_service.make_offer(ctx, s["buyer_owner"], s["buyer"].id, s["player"].id, 300)
    assert unlisted.value.code == "NOT_LISTED"
    with pytest.raises(DomainError):  # el capitán no se lista
        transfer_listing_service.set_listed(ctx, s["seller_owner"], s["seller"].id, s["seller_owner"].id, listed=True)
    transfer_listing_service.set_listed(ctx, s["seller_owner"], s["seller"].id, s["player"].id, listed=True)
    with pytest.raises(ConflictError) as poor:
        transfer_service.make_offer(ctx, s["buyer_owner"], s["buyer"].id, s["player"].id, 5000)
    assert poor.value.code == "INSUFFICIENT_COINS"
    with pytest.raises(ConflictError):  # no se compra a sí mismo
        transfer_service.make_offer(ctx, s["seller_owner"], s["seller"].id, s["player"].id, 10)
    first = transfer_service.make_offer(ctx, s["buyer_owner"], s["buyer"].id, s["player"].id, 100)
    second = transfer_service.make_offer(ctx, s["buyer_owner"], s["buyer"].id, s["player"].id, 200)
    assert (first.status, second.status) == ("WITHDRAWN", "PENDING_OWNER")  # la nueva reemplaza
    transfer_service.withdraw(ctx, s["buyer_owner"], second.id)
    assert second.status == "WITHDRAWN"


def test_balance_is_checked_again_when_player_accepts(ctx, s):
    transfer_listing_service.set_listed(ctx, s["seller_owner"], s["seller"].id, s["player"].id, listed=True)
    offer = transfer_service.make_offer(ctx, s["buyer_owner"], s["buyer"].id, s["player"].id, 900)
    transfer_service.decide_owner(ctx, s["seller_owner"], offer.id, accept=True)
    coin_service.move(ctx, s["buyer"].id, -500, "TEST", None, None)  # el comprador gastó en otra cosa
    with pytest.raises(ConflictError) as poor:
        transfer_service.decide_player(ctx, s["player"], offer.id, accept=True)
    assert poor.value.code == "INSUFFICIENT_COINS"


def test_player_sees_offers_waiting_for_them(ctx, s):
    transfer_listing_service.set_listed(ctx, s["seller_owner"], s["seller"].id, s["player"].id, listed=True)
    offer = transfer_service.make_offer(ctx, s["buyer_owner"], s["buyer"].id, s["player"].id, 300)
    assert manager_queries.my_offers(ctx, s["player"]) == []
    transfer_service.decide_owner(ctx, s["seller_owner"], offer.id, accept=True)
    assert [(o.id, o.to_team.name, o.amount) for o in manager_queries.my_offers(ctx, s["player"])] == [
        (offer.id, "Bravos", 300)]


def test_health_flags_transfer_without_player_consent(ctx, s):
    from app.persistence.models_manager import TransferOffer
    transfer_listing_service.set_listed(ctx, s["seller_owner"], s["seller"].id, s["player"].id, listed=True)
    offer = transfer_service.make_offer(ctx, s["buyer_owner"], s["buyer"].id, s["player"].id, 300)
    ctx.db.execute(TransferOffer.__table__.update().where(TransferOffer.id == offer.id).values(status="COMPLETED"))
    assert [f.code for f in health_service.run_checks(ctx)] == ["TRANSFER_WITHOUT_PLAYER_CONSENT"]
