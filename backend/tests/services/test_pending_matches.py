"""Pendientes de retos y ofertas (Sprint 25) y sus avisos."""

from app.domain.geo import SearchScope
from app.services import match_offer_service, match_request_service, pending_service, push_service
from tests.services.match_helpers import offer_input, request_input, setup_city


def _kinds(ctx, user, kind):
    return [p for p in pending_service.pending(ctx, user) if p.kind == kind]


def test_challenge_is_pending_until_the_target_answers(ctx):
    city = setup_city(ctx)
    (challenger, team), (target_owner, target) = city["uno"], city["dos"]
    request = match_request_service.create_request(
        ctx, challenger, team.id, request_input(ctx, scope=SearchScope.CITY, target=target.id))
    [item] = _kinds(ctx, target_owner, "CHALLENGE_RECEIVED")
    assert (item.title, item.target, item.target_id) == ("Te retaron: Águilas", "feed", target.id)
    assert not _kinds(ctx, challenger, "CHALLENGE_RECEIVED")
    match_offer_service.make_offer(ctx, target_owner, target.id, request.id, offer_input(ctx))
    assert not _kinds(ctx, target_owner, "CHALLENGE_RECEIVED")  # ya respondió
    [offers] = _kinds(ctx, challenger, "OFFERS_RECEIVED")
    assert (offers.title, offers.target, offers.target_id) == ("Ofertas para tu búsqueda (1)", "offers", request.id)


def test_each_new_offer_triggers_a_new_notice(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    push_service.register(ctx, owner, "ExponentPushToken[telefonoDueno01]")
    match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
    [first] = push_service.collect(ctx)
    assert first.body == "Hay ofertas nuevas para tu búsqueda."
    assert push_service.collect(ctx) == []
    match_offer_service.make_offer(ctx, city["tres"][0], city["tres"][1].id, request.id, offer_input(ctx))
    [second] = push_service.collect(ctx)  # «(2)»: una oferta más, un aviso más
    assert second.body == "Hay ofertas nuevas para tu búsqueda."
