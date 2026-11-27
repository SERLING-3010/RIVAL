from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError
from app.services import contract_service, expo_push, push_service
from app.services.push_service import Outgoing
from tests.services.contract_helpers import matched_scene

TOKEN = "ExponentPushToken[telefonoPrueba01]"


def test_register_baselines_and_then_notifies_each_new_pending_once(ctx, clock):
    s = matched_scene(ctx)
    host = s["host_owner"]
    push_service.register(ctx, host, TOKEN)  # ya tenía «firmar contrato»: no se avisa de golpe
    assert push_service.collect(ctx) == []
    for owner in (host, s["guest_owner"]):
        contract_service.sign(ctx, owner, s["contract_id"], version=1)
    clock.advance(timedelta(hours=31))  # el partido ya se jugó: aparece «reportar marcador»
    [notice] = push_service.collect(ctx)
    assert (notice.user_id, notice.tokens, notice.body) == (host.id, [TOKEN], "Hay un marcador por reportar.")
    assert push_service.collect(ctx) == []  # una sola vez por pendiente


def test_token_rules_and_unregister(ctx, clock):
    s = matched_scene(ctx)
    host, guest = s["host_owner"], s["guest_owner"]
    with pytest.raises(DomainError):
        push_service.register(ctx, host, "no-es-un-token")
    push_service.register(ctx, host, TOKEN)
    moved = push_service.register(ctx, guest, TOKEN)  # el mismo teléfono ahora es de otra cuenta
    assert moved.user_id == guest.id
    for i in range(4):
        push_service.register(ctx, guest, f"ExponentPushToken[otroTelefono0{i}]")
    with pytest.raises(ConflictError) as many:
        push_service.register(ctx, guest, "ExponentPushToken[sextoTelefono00]")
    assert many.value.code == "TOO_MANY_DEVICES"
    push_service.unregister(ctx, guest, TOKEN)
    push_service.forget_tokens(ctx, ["ExponentPushToken[otroTelefono00]"])
    assert push_service.collect(ctx) == []


def test_expo_send_batches_and_reports_dead_tokens():
    seen: list[list[dict[str, str]]] = []

    def fake_post(messages):
        seen.append(messages)
        return [{"status": "error", "details": {"error": "DeviceNotRegistered"}} if m["to"].endswith("muerto]")
                else {"status": "ok"} for m in messages]

    dead = expo_push.send([Outgoing(1, ["ExponentPushToken[vivo]", "ExponentPushToken[muerto]"], "Hola.")],
                          post=fake_post)
    assert dead == ["ExponentPushToken[muerto]"]
    assert seen[0][0] == {"to": "ExponentPushToken[vivo]", "title": "RIVAL", "body": "Hola.", "sound": "default",
                          "data": {"open": "pending"}}
