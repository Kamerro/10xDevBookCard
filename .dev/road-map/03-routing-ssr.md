# Routing + SSR

## Routery

- `app/main.py`
  - mount: `/static` → katalog `static/`
  - include: `api_router` (JSON API)
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
    - `books` (placeholder)
    - `selected_book=None`
    - `error_add_book` (dla formularza w sidebar)

- `GET /books/{book_id}`
  - render: `templates/books/detail.html`
  - kontekst:
    - `selected_book` (placeholder)
    - `notes` (placeholder)
    - `edit_note_id` (z query param)
    - `error_add_book`, `error_add_note`, `error_edit_note`

- `POST /books`
  - walidacja title/author
  - w razie błędu: render `books/index.html`
  - sukces: `RedirectResponse(303, /books)`

- `POST /books/{book_id}/notes`
  - walidacja content
  - w razie błędu: render `books/detail.html`
  - sukces: redirect

- `POST /notes/{note_id}`
  - walidacja content
  - w razie błędu: render `books/detail.html` z `edit_note_id`
  - sukces: redirect

## Templaty

- `templates/base.html`
  - layout 2-kolumnowy
  - sidebar: include `templates/partials/_book_list.html`

- `templates/partials/_book_list.html`
  - formularz dodania książki (POST /books)
  - lista książek (placeholder)

- `templates/partials/_note_card.html`
  - karta notatki
  - tryb inline edit sterowany `edit_note_id`

## Static

- CSS: `static/styles.css`
- ładowanie: `<link rel="stylesheet" href="/static/styles.css" />`
