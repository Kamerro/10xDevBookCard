from __future__ import annotations


def test_api_books_requires_auth(client):
    resp = client.get("/api/books")
    assert resp.status_code == 401  # HTTPBearer returns 401 when header missing


def test_api_create_and_list_books(client, auth_header_a):
    create = client.post(
        "/api/books",
        headers=auth_header_a,
        json={"title": "T1", "author": "A1"},
    )
    assert create.status_code == 201
    book_id = create.json()["id"]

    lst = client.get("/api/books", headers=auth_header_a)
    assert lst.status_code == 200
    ids = [b["id"] for b in lst.json()]
    assert book_id in ids


def test_api_book_detail_not_found_for_other_user(client, auth_header_a, auth_header_b):
    create = client.post(
        "/api/books",
        headers=auth_header_a,
        json={"title": "T1", "author": "A1"},
    )
    book_id = create.json()["id"]

    other = client.get(f"/api/books/{book_id}", headers=auth_header_b)
    assert other.status_code == 404


def test_api_create_note_and_update_note(client, auth_header_a):
    book = client.post(
        "/api/books",
        headers=auth_header_a,
        json={"title": "T1", "author": "A1"},
    ).json()
    book_id = book["id"]

    note1 = client.post(
        f"/api/books/{book_id}/notes",
        headers=auth_header_a,
        json={"content": "n1"},
    )
    assert note1.status_code == 201
    n1 = note1.json()
    assert n1["number"] == 1

    note2 = client.post(
        f"/api/books/{book_id}/notes",
        headers=auth_header_a,
        json={"content": "n2"},
    )
    assert note2.status_code == 201
    assert note2.json()["number"] == 2

    upd = client.put(
        f"/api/notes/{n1['id']}",
        headers=auth_header_a,
        json={"content": "n1-updated"},
    )
    assert upd.status_code == 200
    assert upd.json()["content"] == "n1-updated"


def test_api_delete_book_cascades_notes(client, auth_header_a):
    book = client.post(
        "/api/books",
        headers=auth_header_a,
        json={"title": "T1", "author": "A1"},
    ).json()
    book_id = book["id"]

    client.post(
        f"/api/books/{book_id}/notes",
        headers=auth_header_a,
        json={"content": "n1"},
    )

    delete = client.delete(f"/api/books/{book_id}", headers=auth_header_a)
    assert delete.status_code == 200
    assert delete.json()["ok"] is True

    detail = client.get(f"/api/books/{book_id}", headers=auth_header_a)
    assert detail.status_code == 404
