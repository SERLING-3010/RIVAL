"""Rival automático para probar en el teléfono [SIMULACIÓN]. Solo contra la API local de desarrollo.

Usa al usuario de `seed_test_rival.py` y, cada 10 segundos:
- hace una oferta a las búsquedas de partido que ve en su ciudad (incluidos los retos a su equipo);
- firma la versión vigente de cada contrato de su equipo;
- contesta una vez cada mensaje nuevo del chat;
- si el otro equipo ya reportó el resultado, reporta el mismo marcador;
- como dueño del establecimiento de `seed_test_venue.py`, confirma las reservas pendientes.

Uso (con el backend corriendo):  python dev_tools/rival_bot.py
Se detiene con Ctrl+C. Nunca usarlo contra una base con datos reales.
"""

import json
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta

from seed_test_rival import API, EMAIL, PASSWORD
from seed_test_venue import EMAIL as VENUE_EMAIL, PASSWORD as VENUE_PASSWORD

TOKEN = ""
VENUE_TOKEN = ""
REPLY = "¡Listo! Nos vemos en la cancha. (Mensaje automático del rival de prueba)"


def call(method: str, path: str, body: dict[str, object] | None = None, token: str | None = None) -> object:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token or TOKEN}"}
    request = urllib.request.Request(f"{API}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read())


def log(text: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {text}", flush=True)


def offer_to_open_requests(team_id: int, offered: set[int]) -> None:
    for req in call("GET", f"/teams/{team_id}/match-feed?scope=CITY"):  # type: ignore[union-attr]
        if req["id"] in offered:
            continue
        start = max(datetime.fromisoformat(req["window_start"]), datetime.now(UTC) + timedelta(hours=2))
        if start > datetime.fromisoformat(req["window_end"]):
            offered.add(req["id"])
            continue
        mode = "WITHOUT" if req["referee_mode"] == "EITHER" else req["referee_mode"]
        try:
            call("POST", f"/teams/{team_id}/match-requests/{req['id']}/offers", {
                "proposed_start": start.isoformat(), "referee_mode": mode, "place_kind": req["place_kind"],
                "place_note": req["place_note"], "message": "¡Juguemos! (rival de prueba)"})
            log(f"Oferta enviada a la búsqueda {req['id']} de {req['team']['name']} para {start:%d/%m %H:%M} UTC")
        except urllib.error.HTTPError as error:
            log(f"No pude ofertar a la búsqueda {req['id']}: {error.read().decode()[:160]}")
        offered.add(req["id"])


def handle_contracts(team_id: int, replied: set[int]) -> None:
    for summary in call("GET", f"/teams/{team_id}/contracts"):  # type: ignore[union-attr]
        cid = summary["id"]
        contract = call("GET", f"/contracts/{cid}")
        current = contract["current"]  # type: ignore[index]
        if contract["status"] != "CANCELLED" and contract["my_side"] not in current["signed_by"]:  # type: ignore[index]
            try:
                call("POST", f"/contracts/{cid}/sign", {"version": current["version"]})
                log(f"Firmé la versión {current['version']} del contrato {cid}")
            except urllib.error.HTTPError as error:
                log(f"No pude firmar el contrato {cid}: {error.read().decode()[:160]}")
        reply_chat(cid, replied)
        mirror_result(cid, contract)  # type: ignore[arg-type]


def reply_chat(cid: int, replied: set[int]) -> None:
    try:
        page = call("GET", f"/contracts/{cid}/chat")
    except urllib.error.HTTPError:
        return
    for msg in page["messages"]:  # type: ignore[index]
        if not msg["mine"] and not msg["deleted"] and msg["id"] not in replied:
            replied.add(msg["id"])
            if page["writable"]:  # type: ignore[index]
                call("POST", f"/contracts/{cid}/chat", {"text": REPLY})
                log(f"Contesté en el chat del contrato {cid}")


def mirror_result(cid: int, contract: dict[str, object]) -> None:
    result = contract.get("result")
    if not isinstance(result, dict) or result["status"] == "CONFIRMED":
        return
    sides = {r["side"] for r in result["reports"]}
    if result["reports"] and contract["my_side"] not in sides:
        first = result["reports"][0]
        score = {"host_score": first["host_score"], "guest_score": first["guest_score"]}
        call("POST", f"/contracts/{cid}/result", score)
        log(f"Reporté el mismo marcador en el contrato {cid}: {first['host_score']} - {first['guest_score']}")


def confirm_bookings() -> None:
    if not VENUE_TOKEN:
        return
    for venue in call("GET", "/me/venues", token=VENUE_TOKEN):  # type: ignore[union-attr]
        detail = call("GET", f"/venues/{venue['id']}", token=VENUE_TOKEN)
        for booking in detail["pending_bookings"]:  # type: ignore[index]
            call("POST", f"/bookings/{booking['id']}/confirm", token=VENUE_TOKEN)
            log(f"Como dueño de la cancha confirmé la reserva {booking['id']}")


def main() -> None:
    global TOKEN, VENUE_TOKEN
    session = call("POST", "/auth/login", {"email": EMAIL, "password": PASSWORD})
    TOKEN = str(session["token"])  # type: ignore[index]
    try:
        venue_session = call("POST", "/auth/login", {"email": VENUE_EMAIL, "password": VENUE_PASSWORD})
        VENUE_TOKEN = str(venue_session["token"])  # type: ignore[index]
    except urllib.error.HTTPError:
        log("No hay establecimiento de prueba: no confirmaré reservas.")
    teams = call("GET", "/me/teams")
    team_id = int(teams[0]["team"]["id"])  # type: ignore[index]
    log(f"Rival de prueba listo con su equipo {team_id}. Esperando retos, contratos y mensajes...")
    offered: set[int] = set()
    replied: set[int] = set()
    while True:
        try:
            offer_to_open_requests(team_id, offered)
            handle_contracts(team_id, replied)
            confirm_bookings()
        except urllib.error.URLError as error:
            log(f"Sin conexión con el backend: {error}")
        time.sleep(10)


if __name__ == "__main__":
    main()
