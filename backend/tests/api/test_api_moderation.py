"""API de moderación y guardia de suspensión (Sprint 12)."""

from datetime import timedelta

from app.services import sanction_service
from app.services.clock import SystemClock
from app.services.context import ServiceContext
from tests.api.conftest import auth, create_team, register
from tests.conftest import CATALOG


def make_moderator(client, email):
    with client.app.state.session_factory() as session:
        ctx = ServiceContext(db=session, clock=SystemClock(), catalog=CATALOG,
                             session_ttl=timedelta(days=1), session_idle=timedelta(days=1))
        sanction_service.grant_moderator(ctx, email)
        session.commit()


def test_report_suspend_guard_and_appeal(client):
    reporter, rude, mod1, mod2 = (register(client, f"{n}@r.test") for n in ("rep", "rudo", "m1", "m2"))
    for m in ("m1@r.test", "m2@r.test"):
        make_moderator(client, m)
    assert client.get("/api/v1/moderation/reports", headers=auth(reporter["token"])).status_code == 403
    created = client.post("/api/v1/reports", headers=auth(reporter["token"]), json={
        "category": "AGGRESSION", "description": "Me amenazó después del partido", "target_user_id": rude["user"]["id"]})
    assert created.status_code == 201, created.text
    queue = client.get("/api/v1/moderation/reports", headers=auth(mod1["token"])).json()
    assert [r["target"] for r in queue] == ["José Peña"]
    client.post(f"/api/v1/moderation/reports/{queue[0]['id']}/sanction", headers=auth(mod1["token"]),
                json={"kind": "SUSPENSION", "days": 3, "reason": "Amenazas comprobadas"})
    blocked = client.post("/api/v1/teams", headers=auth(rude["token"]), json={
        "name": "Nuevo", "sport_code": "FOOTBALL", "modality_code": "F7", "city": "Barranquilla", "neighborhood": "Centro"})
    assert (blocked.status_code, blocked.json()["code"]) == (403, "ACCOUNT_SUSPENDED")
    me = client.get("/api/v1/moderation/me", headers=auth(rude["token"]))
    assert me.status_code == 200 and me.json()["sanctions"][0]["kind"] == "SUSPENSION"
    sanction_id = me.json()["sanctions"][0]["id"]
    appealed = client.post(f"/api/v1/sanctions/{sanction_id}/appeal", headers=auth(rude["token"]),
                           json={"text": "No fui yo, tengo testigos del partido"})
    assert appealed.status_code == 200, appealed.text
    same = client.post(f"/api/v1/moderation/appeals/{sanction_id}/decide", headers=auth(mod1["token"]),
                       json={"revoke": True})
    assert same.status_code == 403
    client.post(f"/api/v1/moderation/appeals/{sanction_id}/decide", headers=auth(mod2["token"]), json={"revoke": True})
    assert client.post("/api/v1/teams", headers=auth(rude["token"]), json={
        "name": "Nuevo", "sport_code": "FOOTBALL", "modality_code": "F7", "city": "Barranquilla",
        "neighborhood": "Centro"}).status_code == 201


def test_blocks_api(client):
    a, b = register(client, "a@r.test"), register(client, "b@r.test")
    team_a, team_b = create_team(client, a["token"], "Águilas"), create_team(client, b["token"], "Bravos")
    blocked = client.post(f"/api/v1/teams/{team_a}/blocks", headers=auth(a["token"]), json={"team_id": team_b})
    assert [x["team"]["name"] for x in blocked.json()] == ["Bravos"]
    rivals = client.get(f"/api/v1/teams/{team_b}/rivals", headers=auth(b["token"])).json()
    assert rivals["items"] == []
    client.post(f"/api/v1/teams/{team_a}/blocks/{team_b}/remove", headers=auth(a["token"]))
    assert client.get(f"/api/v1/teams/{team_a}/blocks", headers=auth(a["token"])).json() == []
