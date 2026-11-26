import re

import pytest

from app.domain.errors import DomainError
from app.domain.push_rules import GENERIC, MESSAGES, body_for, item_key, validate_token


def test_messages_carry_no_personal_data():
    for text in [*MESSAGES.values(), GENERIC, body_for(["A", "B", "C"])]:
        assert len(text) <= 60
        assert not re.search(r"\d{1,2}:\d{2}|\d+\s*[-–]\s*\d+|@", text)  # sin horas, marcadores ni correos


def test_one_message_per_round():
    assert body_for(["CALLUP"]) == "Tienes una convocatoria nueva."
    assert body_for(["DESCONOCIDO"]) == GENERIC
    assert body_for(["CALLUP", "SIGN_CONTRACT"]) == "Tienes 2 cosas nuevas por revisar en RIVAL."
    assert (item_key("CALLUP", 7), item_key("JOIN_REQUESTS", None)) == ("CALLUP:7", "JOIN_REQUESTS:-")


def test_only_expo_push_tokens():
    assert validate_token(" ExponentPushToken[abcDEF123456_-] ") == "ExponentPushToken[abcDEF123456_-]"
    assert validate_token("ExpoPushToken[abcdefghijkl]") == "ExpoPushToken[abcdefghijkl]"
    for bad in ("", "token", "ExponentPushToken[corto]", "ExponentPushToken[con espacio 123]"):
        with pytest.raises(DomainError) as error:
            validate_token(bad)
        assert error.value.code == "INVALID_PUSH_TOKEN"
