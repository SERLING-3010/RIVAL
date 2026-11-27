"""Envío de avisos por el servicio de Expo (Sprints 24 y 26). Solo va el título, la frase genérica y el
nombre de la pantalla que abre el aviso.

Devuelve los tokens que Expo marcó como dados de baja (DeviceNotRegistered) para borrarlos.
`post` se puede reemplazar en las pruebas: nunca se llama a Expo desde las pruebas.
"""

import json
import urllib.request
from collections.abc import Callable

from app.domain.push_rules import TITLE
from app.services.push_service import Outgoing

EXPO_URL = "https://exp.host/--/api/v2/push/send"
BATCH = 100  # límite de Expo por pedido

Message = dict[str, object]
Post = Callable[[list[Message]], list[dict[str, object]]]


def _post(messages: list[Message]) -> list[dict[str, object]]:
    request = urllib.request.Request(
        EXPO_URL, data=json.dumps(messages).encode(), method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 (URL fija de Expo)
        data = json.loads(response.read()).get("data", [])
    return data if isinstance(data, list) else []


def send(outgoing: list[Outgoing], post: Post = _post) -> list[str]:
    messages: list[Message] = [
        {"to": token, "title": TITLE, "body": o.body, "sound": "default", "data": {"open": o.open}}
        for o in outgoing for token in o.tokens]
    dead = []
    for start in range(0, len(messages), BATCH):
        chunk = messages[start:start + BATCH]
        for message, ticket in zip(chunk, post(chunk)):
            details = ticket.get("details")
            if (ticket.get("status") == "error" and isinstance(details, dict)
                    and details.get("error") == "DeviceNotRegistered"):
                dead.append(str(message["to"]))
    return dead
