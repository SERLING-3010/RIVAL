"""API del check-in en la cancha y de la ubicación del establecimiento (Sprint 15)."""

from tests.api.conftest import auth
from tests.api.test_api_venues import signed_at_venue, venue_with_slot

POSITION = {"latitude": 10.9878, "longitude": -74.7889}


def test_check_in_through_api(client):
    a, b, c, contract_id, kickoff = signed_at_venue(client)
    owner, venue_id, slot_id = venue_with_slot(client, kickoff)
    url = f"/api/v1/contracts/{contract_id}/check-ins"
    board = client.get(url, headers=auth(a["token"])).json()
    assert board["unavailable"] == "Solo hay check-in en partidos con cancha reservada y confirmada."
    booked = client.post(f"/api/v1/contracts/{contract_id}/bookings", headers=auth(b["token"]), json={"slot_id": slot_id})
    booking_id = booked.json()["booking"]["id"]
    client.post(f"/api/v1/bookings/{booking_id}/confirm", headers=auth(owner["token"]))
    assert client.post(f"/api/v1/venues/{venue_id}/location", headers=auth(a["token"]), json=POSITION).status_code == 403
    bad = client.post(f"/api/v1/venues/{venue_id}/location", headers=auth(owner["token"]),
                      json={"latitude": 120, "longitude": 0})
    assert bad.status_code == 422
    saved = client.post(f"/api/v1/venues/{venue_id}/location", headers=auth(owner["token"]), json=POSITION)
    assert saved.json() == {"has_location": True}
    assert client.get(f"/api/v1/venues/{venue_id}", headers=auth(owner["token"])).json()["has_location"]
    board = client.get(url, headers=auth(a["token"])).json()
    assert (board["unavailable"], board["venue_name"], board["window_open"]) == (None, "Canchas El Prado", False)
    early = client.post(url, headers=auth(a["token"]), json=POSITION)  # el partido es mañana
    assert (early.status_code, early.json()["code"]) == (409, "CHECKIN_NOT_OPEN")
    assert client.get(url, headers=auth(c["token"])).status_code == 404  # no juega este partido
