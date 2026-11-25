from datetime import timedelta

import pytest
from sqlalchemy import select

from app.domain.errors import ConflictError, PermissionDeniedError
from app.persistence.models_audit import AuditEvent
from app.persistence.models_contracts import MatchContract
from app.services import contract_service, fixture_service, league_queries, season_service, team_card_service
from tests.services.league_match_helpers import first_kickoff, league_with_teams, play


def owner_of(s, team_id):
    return next(o for o, t in s["teams"].values() if t.id == team_id)


def _season(ctx, clock):
    s = league_with_teams(ctx)
    fixtures = fixture_service.generate(ctx, s["organizer"], s["league"].id, first_kickoff(ctx), 7)
    return s, [ctx.db.get(MatchContract, f.contract_id) for f in fixtures]


def test_season_closes_only_when_finished_and_crowns_the_leader(ctx, clock):
    s, contracts = _season(ctx, clock)
    with pytest.raises(PermissionDeniedError):
        season_service.close(ctx, s["teams"]["b"][0], s["league"].id)
    with pytest.raises(ConflictError) as early:
        season_service.close(ctx, s["organizer"], s["league"].id)
    assert early.value.code == "SEASON_NOT_FINISHED"
    a_id = s["teams"]["a"][1].id
    last = contracts[-1]  # se cancela antes de jugarse: un partido cancelado no bloquea el cierre
    contract_service.cancel(ctx, owner_of(s, last.host_team_id), last.id, "No hubo cancha disponible")
    for contract in contracts[:-1]:
        owners = [owner_of(s, contract.host_team_id), owner_of(s, contract.guest_team_id)]
        a_hosts = contract.host_team_id == a_id
        play(ctx, clock, contract, owners, 3 if a_hosts else 0, 0 if a_hosts else 3)
        clock.advance(timedelta(days=5))  # la siguiente fecha es una semana después
    league = season_service.close(ctx, s["organizer"], s["league"].id)
    assert league.champion_team_id == a_id and league.closed_at is not None
    detail = league_queries.league_detail(ctx, s["organizer"], s["league"].id)
    assert detail.champion is not None and detail.champion.name == "Águilas"
    with pytest.raises(ConflictError) as twice:
        season_service.close(ctx, s["organizer"], s["league"].id)
    assert twice.value.code == "SEASON_ALREADY_CLOSED"
    event = ctx.db.scalars(select(AuditEvent).where(AuditEvent.action == "LEAGUE_SEASON_CLOSED")).one()
    assert event.initiated_by == s["organizer"].id


def test_team_card_counts_titles_and_keeps_specials(ctx, clock):
    s, contracts = _season(ctx, clock)
    team = s["teams"]["a"][1]
    card = team_card_service.card(ctx, team, 88)
    assert (card.tier, card.display_tier, card.leagues) == ("ORO_BRILLANTE", "ORO_BRILLANTE", 0)
    s["league"].champion_team_id = team.id  # campeón de liga, sin pasar por el cierre (atajo de prueba)
    ctx.db.flush()
    card = team_card_service.card(ctx, team, 88)
    prisma = next(sp for sp in card.specials if sp.code == "PRISMA")
    assert (card.leagues, prisma.earned_at is not None, card.display_tier) == (1, True, "PRISMA")
    later = team_card_service.card(ctx, team, 60)  # la media baja: la especial se queda
    assert (later.tier, later.display_tier) == ("BRONCE", "PRISMA")
    assert len(contracts) == 3


def test_only_the_admin_changes_crest_and_design(ctx, clock):
    from app.domain.errors import DomainError
    from app.services import team_look_service

    s, _contracts = _season(ctx, clock)
    owner, team = s["teams"]["a"]
    with pytest.raises(PermissionDeniedError):
        team_look_service.set_crest(ctx, s["teams"]["b"][0], team.id, "ESCUDO|#0B6B3A|#F6DE92|ESTRELLA")
    team_look_service.set_crest(ctx, owner, team.id, "ESCUDO|#0B6B3A|#F6DE92|ESTRELLA")
    assert team.crest == "ESCUDO|#0B6B3A|#F6DE92|ESTRELLA"
    with pytest.raises(DomainError) as not_owned:
        team_look_service.set_card_choice(ctx, owner, team.id, "PRISMA")
    assert not_owned.value.code == "DESIGN_NOT_OWNED"
    s["league"].champion_team_id = team.id
    ctx.db.flush()
    assert team_card_service.card(ctx, team, 88).available == ["BASIC", "PRISMA"]
    team_look_service.set_card_choice(ctx, owner, team.id, "BASIC")  # prefiere mostrar su básica
    assert team_card_service.card(ctx, team, 88).display_tier == "ORO_BRILLANTE"
    actions = [e.action for e in ctx.db.scalars(select(AuditEvent).where(AuditEvent.entity == "team"))]
    assert {"TEAM_CREST_CHANGED", "TEAM_DESIGN_CHOSEN"} <= set(actions)
