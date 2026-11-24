"""Ayudas de pruebas de establecimientos: dueño con cancha y partidos firmados en cancha [SIMULACIÓN]."""

from datetime import timedelta
from decimal import Decimal

from app.domain.geo import SearchScope
from app.domain.match_rules import PlaceKind
from app.domain.roles import UserRole
from app.services import auth_service, contract_queries, contract_service, match_offer_service, match_request_service
from app.services import venue_service
from app.services.venue_views import CourtInput, VenueInput
from tests.conftest import register_input
from tests.services.contract_helpers import changed_terms, matched_scene
from tests.services.match_helpers import offer_input, request_input


def venue_owner(ctx, email="cancha@r.test"):
    return auth_service.register_user(ctx, register_input(email=email, role=UserRole.VENUE_OWNER))


def venue_input(**changes):
    data = {"name": "Canchas El Prado", "address": "Calle 72 # 45-10", "city": "Ciudad Prueba",
            "neighborhood": "Barrio Uno", "reference_price": Decimal("80000")}
    return VenueInput(**{**data, **changes})


def venue_with_court(ctx, owner=None):
    owner = owner or venue_owner(ctx)
    venue = venue_service.create_venue(ctx, owner, venue_input())
    court = venue_service.add_court(ctx, owner, venue.id, CourtInput(name="Cancha 1", sport_code="FOOTBALL",
                                                                     surface="Sintética"))
    return owner, venue, court


def accepted_contract(ctx, host, guest):
    """El primero publica, el segundo oferta (en 30 h) y el primero acepta. Devuelve el id del contrato."""
    (host_owner, host_team), (guest_owner, guest_team) = host, guest
    request = match_request_service.create_request(ctx, host_owner, host_team.id,
                                                   request_input(ctx, scope=SearchScope.CITY))
    offer = match_offer_service.make_offer(ctx, guest_owner, guest_team.id, request.id, offer_input(ctx))
    match_offer_service.decide(ctx, host_owner, offer.id, accept=True)
    return contract_queries.contract_id_for_offer(ctx, offer.id)


def sign_at_venue(ctx, host_owner, guest_owner, contract_id):
    terms = changed_terms(ctx, host_owner, contract_id, place_kind=PlaceKind.VENUE)
    contract_service.propose(ctx, host_owner, contract_id, base_version=1, terms=terms)
    contract_service.sign(ctx, guest_owner, contract_id, version=2)
    return terms.kickoff_at


def signed_venue_match(ctx):
    """Águilas contra Bravos, firmado en cancha de establecimiento; empieza en 30 h y dura 60 min."""
    scene = matched_scene(ctx)
    scene["kickoff"] = sign_at_venue(ctx, scene["host_owner"], scene["guest_owner"], scene["contract_id"])
    return scene


def slot_around(ctx, owner, court, kickoff, before=30, after=90):
    return venue_service.add_slot(ctx, owner, court.id, kickoff - timedelta(minutes=before),
                                  kickoff + timedelta(minutes=after))
