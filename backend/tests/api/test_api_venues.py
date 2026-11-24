"""API de establecimientos y reservas (Sprint 6)."""

from datetime import datetime, timedelta

from tests.api.conftest import auth, register
from tests.api.test_api_contracts import matched


def venue_with_slot(client, kickoff: datetime):
    owner = register(client, "cancha@r.test", "VENUE_OWNER")
    created = client.post("/api/v1/venues", headers=auth(owner["token"]), json={
        "name": "Canchas El Prado", "address": "Calle 72 # 45-10", "city": "Barranquilla",
        "neighborhood": "El Prado", "reference_price": "80000.50"})
    assert created.status_code == 201, created.text
    venue_id = created.json()["venue"]["id"]
    assert created.json()["venue"]["reference_price"] == "80000.50"  # decimal exacto, como texto
    court = client.post(f"/api/v1/venues/{venue_id}/courts", headers=auth(owner["token"]),
                        json={"name": "Cancha 1", "sport_code": "FOOTBALL", "surface": "Sintética"})
    court_id = court.json()["courts"][0]["id"]
    slot = client.post(f"/api/v1/courts/{court_id}/slots", headers=auth(owner["token"]), json={
        "starts_at": (kickoff - timedelta(minutes=30)).isoformat(),
        "ends_at": (kickoff + timedelta(minutes=90)).isoformat()})
    assert slot.status_code == 201, slot.text
    return owner, venue_id, slot.json()["slots"][0]["id"]


def signed_at_venue(client):
    a, b, c, team_a, contract_id = matched(client)
    detail = client.get(f"/api/v1/contracts/{contract_id}", headers=auth(a["token"])).json()
    terms = {**detail["current"]["terms"], "place_kind": "VENUE"}
    client.post(f"/api/v1/contracts/{contract_id}/proposals", headers=auth(a["token"]),
                json={"base_version": 1, "terms": terms})
    client.post(f"/api/v1/contracts/{contract_id}/sign", headers=auth(b["token"]), json={"version": 2})
    return a, b, c, contract_id, datetime.fromisoformat(terms["kickoff_at"])


def test_book_confirm_and_ready_to_play(client):
    a, b, _c, contract_id, kickoff = signed_at_venue(client)
    owner, venue_id, slot_id = venue_with_slot(client, kickoff)
    found = client.get("/api/v1/venues", params={"city": "barranquilla", "sport": "FOOTBALL"}, headers=auth(b["token"]))
    assert [v["id"] for v in found.json()["items"]] == [venue_id]
    booked = client.post(f"/api/v1/contracts/{contract_id}/bookings", headers=auth(b["token"]), json={"slot_id": slot_id})
    assert booked.status_code == 201, booked.text
    assert (booked.json()["booking"]["status"], booked.json()["ready_to_play"]) == ("PENDING", False)
    owner_view = client.get(f"/api/v1/venues/{venue_id}", headers=auth(owner["token"])).json()
    booking_id = owner_view["pending_bookings"][0]["id"]
    assert client.post(f"/api/v1/bookings/{booking_id}/confirm", headers=auth(a["token"])).status_code == 403
    confirmed = client.post(f"/api/v1/bookings/{booking_id}/confirm", headers=auth(owner["token"]))
    assert [x["id"] for x in confirmed.json()["confirmed_bookings"]] == [booking_id]
    contract = client.get(f"/api/v1/contracts/{contract_id}", headers=auth(a["token"])).json()
    assert (contract["booking"]["venue_name"], contract["ready_to_play"]) == ("Canchas El Prado", True)


def test_rules_through_api(client):
    a, _b, c, contract_id, kickoff = signed_at_venue(client)
    owner, venue_id, slot_id = venue_with_slot(client, kickoff)
    assert client.post("/api/v1/venues", headers=auth(a["token"]), json={
        "name": "Mi cancha", "address": "Calle 1 # 2-3", "city": "Barranquilla", "neighborhood": "Centro"}
    ).status_code == 403
    bad_price = client.post("/api/v1/venues", headers=auth(owner["token"]), json={
        "name": "Otra", "address": "Calle 1 # 2-3", "city": "Barranquilla", "neighborhood": "Centro",
        "reference_price": "10.555"})
    assert bad_price.status_code == 422
    outsider = client.post(f"/api/v1/contracts/{contract_id}/bookings", headers=auth(c["token"]), json={"slot_id": slot_id})
    assert outsider.status_code == 404
    booked = client.post(f"/api/v1/contracts/{contract_id}/bookings", headers=auth(a["token"]), json={"slot_id": slot_id})
    booking_id = booked.json()["booking"]["id"]
    cancelled = client.post(f"/api/v1/bookings/{booking_id}/cancel", headers=auth(a["token"]))
    assert (cancelled.status_code, cancelled.json()["booking"]["status"]) == (200, "CANCELLED")
