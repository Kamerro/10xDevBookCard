from __future__ import annotations


def _login(client, *, email: str, password: str):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def test_ssr_books_requires_cookie_redirects_to_login(client):
    resp = client.get("/books", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


def test_ssr_login_sets_cookie_and_redirects(client, user_a):
    resp = _login(client, email=user_a.email, password="Password1!")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/books"
    set_cookie = resp.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie


def test_ssr_login_invalid_renders_error(client, user_a):
    resp = client.post(
        "/login",
        data={"email": user_a.email, "password": "WrongPassword1!"},
    )
    assert resp.status_code == 200
    assert "Nieprawidłowy email lub hasło" in resp.text


def test_ssr_create_book_validation_error(client, user_a):
    login = _login(client, email=user_a.email, password="Password1!")
    cookie = login.headers["set-cookie"].split(";", 1)[0]

    resp = client.post(
        "/books",
        data={"title": "", "author": ""},
        headers={"Cookie": cookie},
    )
    assert resp.status_code == 200
    assert "Tytuł i autor są wymagane" in resp.text


def test_ssr_create_book_and_note_flow(client, user_a):
    login = _login(client, email=user_a.email, password="Password1!")
    cookie = login.headers["set-cookie"].split(";", 1)[0]

    created = client.post(
        "/books",
        data={"title": "T1", "author": "A1"},
        headers={"Cookie": cookie},
        follow_redirects=False,
    )
    assert created.status_code == 303
    assert created.headers["location"] == "/books"

    index = client.get("/books", headers={"Cookie": cookie})
    assert index.status_code == 200
    assert "T1" in index.text

    import re

    m = re.search(r"/books/([0-9a-fA-F-]{36})", index.text)
    assert m is not None
    book_id = m.group(1)

    note = client.post(
        f"/books/{book_id}/notes",
        data={"content": "n1"},
        headers={"Cookie": cookie},
        follow_redirects=False,
    )
    assert note.status_code == 303
    assert note.headers["location"] == f"/books/{book_id}"

    detail = client.get(f"/books/{book_id}", headers={"Cookie": cookie})
    assert detail.status_code == 200
    assert "n1" in detail.text
