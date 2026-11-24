"""Ayudas para pruebas de partidos con catálogo SINTÉTICO [SIMULACIÓN]."""

from datetime import timedelta

from app.domain.geo import SearchScope
from app.domain.match_rules import PlaceKind, RefereeMode
from app.services import neighborhood_service
from app.services.match_views import MatchRequestInput, OfferInput
from tests.services.test_neighborhood_service import SYNTHETIC_CSV
from tests.services.test_rival_service import make_team


def setup_city(ctx):
    neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
    return {
        "uno": make_team(ctx, "uno@r.test", "Águilas", "Barrio Uno"),
        "dos": make_team(ctx, "dos@r.test", "Bravos", "Barrio Dos"),
        "tres": make_team(ctx, "tres@r.test", "Cóndores", "Barrio Tres"),
        "lejos": make_team(ctx, "lejos@r.test", "Lejanos", "Barrio Lejano"),
    }


def request_input(ctx, scope=SearchScope.NEARBY, radius=2, referee=RefereeMode.EITHER, target=None):
    now = ctx.clock.now()
    return MatchRequestInput(
        window_start=now + timedelta(days=1), window_end=now + timedelta(days=3), scope=scope,
        referee_mode=referee, place_kind=PlaceKind.INFORMAL, radius_km=radius if scope == SearchScope.NEARBY else None,
        target_team_id=target, place_note="Parque del barrio", message="Partido amistoso",
    )


def offer_input(ctx, hours=30, referee=RefereeMode.WITHOUT):
    return OfferInput(proposed_start=ctx.clock.now() + timedelta(hours=hours), referee_mode=referee,
                      place_kind=PlaceKind.INFORMAL, place_note="Cancha de arena")
