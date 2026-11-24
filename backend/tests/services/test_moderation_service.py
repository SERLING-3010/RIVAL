from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.domain.moderation_rules import ReportCategory, SanctionKind
from app.services import appeal_service, report_service, sanction_service
from tests.services.test_rival_service import make_team
from tests.services.test_team_service import new_user


@pytest.fixture
def s(ctx):
    reporter, team = make_team(ctx, "rep@r.test", "Águilas", "Barrio Uno")
    rude, rude_team = make_team(ctx, "rudo@r.test", "Bravos", "Barrio Dos")
    mods = [new_user(ctx, f"mod{i}@r.test") for i in range(2)]
    for m in mods:
        sanction_service.grant_moderator(ctx, m.email)
    return {"reporter": reporter, "team": team, "rude": rude, "rude_team": rude_team, "mods": mods}


def report(ctx, s, **target):
    return report_service.create_report(ctx, s["reporter"], category=ReportCategory.AGGRESSION,
                                        description="Insultó al árbitro y empujó a un rival", **target)


def test_report_rules(ctx, s):
    with pytest.raises(DomainError):
        report_service.create_report(ctx, s["reporter"], category=ReportCategory.OTHER, description="corto",
                                     target_user_id=s["rude"].id)
    with pytest.raises(DomainError) as self_report:
        report(ctx, s, target_user_id=s["reporter"].id)
    assert self_report.value.code == "INVALID_REPORT_TARGET"
    with pytest.raises(DomainError):  # tampoco a su propio equipo
        report(ctx, s, target_team_id=s["team"].id)
    for _ in range(5):
        report(ctx, s, target_user_id=s["rude"].id)
    with pytest.raises(ConflictError) as quota:
        report(ctx, s, target_user_id=s["rude"].id)
    assert quota.value.code == "TOO_MANY_REPORTS"


def test_only_moderators_see_queue_and_decide(ctx, s):
    r = report(ctx, s, target_user_id=s["rude"].id)
    with pytest.raises(PermissionDeniedError):
        sanction_service.queue(ctx, s["reporter"])
    assert [q.id for q in sanction_service.queue(ctx, s["mods"][0])] == [r.id]
    sanction_service.dismiss(ctx, s["mods"][0], r.id, "Sin pruebas suficientes")
    assert sanction_service.queue(ctx, s["mods"][0]) == []


def test_suspension_and_four_eyes_appeal(ctx, s, clock):
    r = report(ctx, s, target_team_id=s["rude_team"].id)  # contra el equipo: se sanciona a su administrador
    sanction = sanction_service.sanction(ctx, s["mods"][0], r.id, SanctionKind.SUSPENSION, 7, "Agresión comprobada")
    assert sanction.user_id == s["rude"].id
    assert sanction_service.active_suspension(ctx, s["rude"].id) is not None
    appeal_service.appeal(ctx, s["rude"], sanction.id, "Fue un malentendido, tengo testigos del partido")
    with pytest.raises(ConflictError):  # una sola apelación
        appeal_service.appeal(ctx, s["rude"], sanction.id, "Otra vez lo mismo, por favor revisen")
    with pytest.raises(PermissionDeniedError) as same:
        appeal_service.decide_appeal(ctx, s["mods"][0], sanction.id, revoke=True)
    assert same.value.code == "FOUR_EYES_REQUIRED"
    assert [a.id for a in appeal_service.appeals_queue(ctx, s["mods"][1])] == [sanction.id]
    assert appeal_service.appeals_queue(ctx, s["mods"][0]) == []
    appeal_service.decide_appeal(ctx, s["mods"][1], sanction.id, revoke=True)
    assert sanction_service.active_suspension(ctx, s["rude"].id) is None


def test_suspension_expires_and_warning_does_not_suspend(ctx, s, clock):
    r1, r2 = report(ctx, s, target_user_id=s["rude"].id), report(ctx, s, target_user_id=s["rude"].id)
    sanction_service.sanction(ctx, s["mods"][0], r1.id, SanctionKind.WARNING, None, "Primera advertencia")
    assert sanction_service.active_suspension(ctx, s["rude"].id) is None
    with pytest.raises(DomainError):
        sanction_service.sanction(ctx, s["mods"][0], r2.id, SanctionKind.SUSPENSION, 45, "Demasiado largo")
    sanction_service.sanction(ctx, s["mods"][0], r2.id, SanctionKind.SUSPENSION, 2, "Reincidencia")
    clock.advance(timedelta(days=3))
    assert sanction_service.active_suspension(ctx, s["rude"].id) is None
    assert [x.kind for x in sanction_service.my_sanctions(ctx, s["rude"])] == ["SUSPENSION", "WARNING"]


def test_moderator_cannot_decide_reports_about_themselves(ctx, s):
    r = report_service.create_report(ctx, s["rude"], category=ReportCategory.OTHER,
                                     description="El moderador me trató mal en un partido", target_user_id=s["mods"][0].id)
    assert sanction_service.queue(ctx, s["mods"][0]) == []
    with pytest.raises(PermissionDeniedError):
        sanction_service.dismiss(ctx, s["mods"][0], r.id, "No aplica")
