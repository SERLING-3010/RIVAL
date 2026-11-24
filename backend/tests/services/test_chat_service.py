from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.domain.moderation_rules import ReportCategory
from app.persistence.models_league_matches import RefereeAssignment
from app.services import chat_moderation, chat_service, contract_service, report_service, sanction_service
from tests.services.contract_helpers import matched_scene
from tests.services.manager_helpers import add_player
from tests.services.test_team_service import new_user


@pytest.fixture
def s(ctx):
    return matched_scene(ctx)  # Águilas (local) vs Bravos, partido en unas 30 horas


def test_only_participants_read_and_write(ctx, s, clock):
    host_player = add_player(ctx, s["host"], "compa@r.test")
    stranger = new_user(ctx, "extrano@r.test")
    chat_service.post(ctx, s["host_owner"], s["contract_id"], "  ¿Quién lleva   el balón?  ")
    chat_service.post(ctx, s["guest_owner"], s["contract_id"], "Nosotros")
    page = chat_service.read(ctx, host_player, s["contract_id"])
    assert [m.body for m in page.messages] == ["¿Quién lleva el balón?", "Nosotros"]
    assert page.writable and not page.messages[0].mine
    assert [m.body for m in chat_service.read(ctx, host_player, s["contract_id"], page.messages[0].id).messages] == [
        "Nosotros"]
    for action in (lambda: chat_service.read(ctx, stranger, s["contract_id"]),
                   lambda: chat_service.post(ctx, stranger, s["contract_id"], "hola")):
        with pytest.raises(NotFoundError):
            action()


def test_referee_is_a_participant(ctx, s, clock):
    referee = new_user(ctx, "pito@r.test")
    ctx.db.add(RefereeAssignment(contract_id=s["contract_id"], referee_id=referee.id, status="PENDING",
                                 assigned_by=s["host_owner"].id, assigned_at=clock.now()))
    ctx.db.flush()
    chat_service.post(ctx, referee, s["contract_id"], "Llego 20 minutos antes")


def test_text_rate_and_window(ctx, s, clock):
    with pytest.raises(DomainError):
        chat_service.post(ctx, s["host_owner"], s["contract_id"], "   ")
    with pytest.raises(DomainError):
        chat_service.post(ctx, s["host_owner"], s["contract_id"], "x" * 501)
    for i in range(10):
        chat_service.post(ctx, s["host_owner"], s["contract_id"], f"mensaje {i}")
    with pytest.raises(ConflictError) as rate:
        chat_service.post(ctx, s["host_owner"], s["contract_id"], "uno más")
    assert rate.value.code == "TOO_MANY_MESSAGES"
    clock.advance(timedelta(minutes=2))
    chat_service.post(ctx, s["host_owner"], s["contract_id"], "ya puedo")
    clock.advance(timedelta(hours=80))  # más de 48 h después del partido
    assert not chat_service.read(ctx, s["host_owner"], s["contract_id"]).writable
    with pytest.raises(ConflictError) as closed:
        chat_service.post(ctx, s["host_owner"], s["contract_id"], "tarde")
    assert closed.value.code == "CHAT_CLOSED"


def test_cancelled_match_is_read_only(ctx, s):
    contract_service.cancel(ctx, s["host_owner"], s["contract_id"], "Se cruzó con otro torneo")
    with pytest.raises(ConflictError):
        chat_service.post(ctx, s["guest_owner"], s["contract_id"], "¿Y ahora?")


def test_delete_hides_text_but_moderation_sees_it_with_an_open_report(ctx, s):
    message = chat_service.post(ctx, s["guest_owner"], s["contract_id"], "Mensaje ofensivo")
    with pytest.raises(PermissionDeniedError):
        chat_service.delete(ctx, s["host_owner"], message.id)
    chat_service.delete(ctx, s["guest_owner"], message.id)
    shown = chat_service.read(ctx, s["host_owner"], s["contract_id"]).messages[0]
    assert (shown.deleted, shown.body) == (True, None)
    mod = new_user(ctx, "mod@r.test")
    sanction_service.grant_moderator(ctx, mod.email)
    with pytest.raises(NotFoundError):  # sin reporte abierto no hay lectura
        chat_moderation.read_for_report(ctx, mod, s["contract_id"])
    report_service.create_report(ctx, s["host_owner"], category=ReportCategory.AGGRESSION,
                                 description="Nos insultó por el chat del partido",
                                 target_user_id=s["guest_owner"].id, contract_id=s["contract_id"])
    with pytest.raises(PermissionDeniedError):  # quien no es moderador
        chat_moderation.read_for_report(ctx, s["host_owner"], s["contract_id"])
    page = chat_moderation.read_for_report(ctx, mod, s["contract_id"])
    assert [(m.body, m.deleted) for m in page.messages] == [("Mensaje ofensivo", True)] and not page.writable
