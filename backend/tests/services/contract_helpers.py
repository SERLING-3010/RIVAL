"""Ayudas para pruebas del contrato: dos equipos con una oferta aceptada [SIMULACIÓN]."""

from dataclasses import replace

from app.domain.geo import SearchScope
from app.services import contract_queries, match_offer_service, match_request_service
from tests.services.match_helpers import offer_input, request_input, setup_city


def matched_scene(ctx):
    """Águilas (local) publica; Bravos (visitante) oferta; Águilas acepta. Devuelve ids y dueños."""
    city = setup_city(ctx)
    host_owner, host = city["uno"]
    guest_owner, guest = city["dos"]
    request = match_request_service.create_request(ctx, host_owner, host.id, request_input(ctx, scope=SearchScope.CITY))
    offer = match_offer_service.make_offer(ctx, guest_owner, guest.id, request.id, offer_input(ctx))
    match_offer_service.decide(ctx, host_owner, offer.id, accept=True)
    contract_id = contract_queries.team_contracts(ctx, host_owner, host.id)[0].id
    return {"city": city, "host_owner": host_owner, "guest_owner": guest_owner, "host": host, "guest": guest,
            "contract_id": contract_id, "request": request, "offer": offer}


def current_terms(ctx, actor, contract_id):
    return contract_queries.get_contract(ctx, actor, contract_id).current.terms


def changed_terms(ctx, actor, contract_id, **changes):
    return replace(current_terms(ctx, actor, contract_id), **changes)
