"""Cartas especiales al momento y su aviso (Sprint 26)."""

from sqlalchemy import select

from app.domain import special_cards, team_special_cards
from app.domain.push_rules import open_for
from app.persistence.models_cards import SpecialCard, TeamSpecialCard
from app.persistence.models_push import PushSent
from app.services import lineup_service, push_service
from tests.services.manager_helpers import confirmed_match

TOKEN = "ExponentPushToken[telefonoCartas01]"


def _easy_rubi(monkeypatch):
    """Rubí con requisitos mínimos, solo para la prueba: media 0 y 1 gol / 1 victoria."""
    easy = ("RUBI", 0, [("1 gol", lambda f: f.goals, 1)])
    monkeypatch.setattr(special_cards, "SPECIALS", [easy, *special_cards.SPECIALS[1:]])
    team_easy = ("RUBI", 0, [("1 victoria", lambda f: f.wins, 1)])
    monkeypatch.setattr(team_special_cards, "TEAM_SPECIALS", [team_easy, *team_special_cards.TEAM_SPECIALS[1:]])


def test_lineup_awards_player_and_team_cards_without_opening_any_screen(ctx, clock, monkeypatch):
    s = confirmed_match(ctx, clock, 2, 1)
    host = s["host_owner"]
    push_service.register(ctx, host, TOKEN)  # lo que ya hubiera, no se avisa
    _easy_rubi(monkeypatch)
    lineup_service.record(ctx, host, s["contract_id"], [(host.id, 2)])
    assert ctx.db.scalar(select(SpecialCard.code).where(SpecialCard.user_id == host.id)) == "RUBI"
    assert ctx.db.scalar(select(TeamSpecialCard.code).where(TeamSpecialCard.team_id == s["host"].id)) == "RUBI"
    [notice] = push_service.collect(ctx)
    keys = set(ctx.db.scalars(select(PushSent.item_key).where(PushSent.user_id == host.id)))
    assert {"CARD:RUBI", f"TEAMCARD:{s['host'].id}:RUBI"} <= keys
    assert notice.user_id == host.id
    assert push_service.collect(ctx) == []  # una sola vez


def test_where_a_notice_opens():
    assert open_for(["NEW_CARD"]) == "myCard"
    assert open_for(["TEAM_NEW_CARD"]) == "home"
    assert open_for(["NEW_CARD", "CALLUP"]) == "pending"
