from __future__ import annotations


def test_api_health_db_ok(client):
    resp = client.get("/api/health/db")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
