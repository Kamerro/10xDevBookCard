# Routing + SSR

## Routery

- `app/main.py`
  - mount: `/static` → katalog `static/`
  - include: `api_router` (JSON API) pod prefixem `/api`
  - include: `web_router` (SSR)

- `app/api/router.py`
  - miejsce na JSON API (auth/books/notes)

- `app/web/router.py`
  - router SSR
  - aktualnie zawiera `app/web/books.py`

## SSR endpoints (dzisiaj)

- `GET /books`
  - render: `templates/books/index.html`
  - kontekst:
    - `books` (z DB)
    - `selected_book=None`
    - `error_add_book` (dla formularza w sidebar)

- `GET /books/{book_id}`
  - render: `templates/books/detail.html`
  - kontekst:
    - `selected_book` (z DB)
    - `notes` (z DB)
    - `edit_note_id` (z query param)
    - `error_add_book`, `error_add_note`, `error_edit_note`

- `POST /books`
  - walidacja title/author
  - w razie błędu: render `books/index.html`
  - sukces: `RedirectResponse(303, /books)`
  - zapis do DB (service: `app/services/book_service.py`)

- `POST /books/{book_id}/notes`
  - walidacja content
  - w razie błędu: render `books/detail.html`
  - sukces: redirect
  - zapis do DB (service: `app/services/note_service.py`)

- `POST /notes/{note_id}`
  - walidacja content
  - w razie błędu: render `books/detail.html` z `edit_note_id`
  - sukces: redirect
  - zapis do DB (service: `app/services/note_service.py`)

## JSON API (dzisiaj)

- Wszystkie endpointy z `app/api/*` są dostępne pod prefixem `/api`.
- Przykład: `GET /api/books`, `POST /api/books/{book_id}/notes`.

## Templaty

- `templates/base.html`
  - layout 2-kolumnowy
  - sidebar: include `templates/partials/_book_list.html`

- `templates/partials/_book_list.html`
  - formularz dodania książki (POST /books)
  - lista książek (z DB)

- `templates/partials/_note_card.html`
  - karta notatki
  - tryb inline edit sterowany `edit_note_id`

## Static

- CSS: `static/styles.css`
- ładowanie: `<link rel="stylesheet" href="/static/styles.css" />`
