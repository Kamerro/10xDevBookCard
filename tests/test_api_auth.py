from __future__ import annotations


def test_api_register_success(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "Password1!", "password_confirm": "Password1!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


def test_api_register_password_mismatch(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "x@example.com", "password": "Password1!", "password_confirm": "Password2!"},
    )
    assert resp.status_code == 400


def test_api_login_success(client, user_a):
    resp = client.post(
        "/api/auth/login",
        json={"email": user_a.email, "password": "Password1!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("access_token"), str)
    assert data.get("token_type") == "bearer"


def test_api_login_invalid_credentials(client, user_a):
    resp = client.post(
        "/api/auth/login",
        json={"email": user_a.email, "password": "WrongPassword1!"},
    )
    assert resp.status_code == 401
