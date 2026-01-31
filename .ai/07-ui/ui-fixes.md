# UI Fixes Plan (SSR)

 > **Najważniejsze dokumenty (source of truth)**
 > - [GOVERNANCE](./GOVERNANCE.md)
 > - [PRD](./prd.md)

## Cel

- Root `/` ma wyświetlać **Login/Register na środku** (bez linków typu „przejdź do książek”).
- Po zalogowaniu:
  - w **lewym górnym rogu**: `Wyloguj`
  - na **środku strony lub po lewej**: lista książek + formularz dodania książki
- Naprawić bug: **"Edytuj notatkę" odpala dodanie nowej notatki** (edycja nie wchodzi w tryb edycji).

## Aktualny stan (źródła)

- Root: `app/web/home.py` renderuje `templates/home.html` (extends `base_public.html`).
- Layout zalogowany: `templates/base.html` zawsze pokazuje sidebar z `partials/_book_list.html` + przycisk `Wyloguj`.
- Widok książki: `templates/books/detail.html` + `partials/_note_card.html`.

## Zmiana 1 — Root: login/register na środku

### Wymaganie

- `/` ma być stroną „auth landing” — na środku dwa przyciski lub dwa formularze.

### Proponowana implementacja

Opcja MVP (najmniej ryzykowna):

- Zmienić `templates/home.html`:
  - usunąć link `Przejdź do książek`
  - zostawić tylko CTA: `Zaloguj się` i `Załóż konto`
  - dodać proste wycentrowanie (CSS/class)

Opcja docelowa (lepszy UX):

- Nowy template np. `templates/auth/landing.html` (extends `base_public.html`)
  - 2 kolumny / tabs: Login i Register na środku
  - wysyła na istniejące endpointy: `POST /login` i `POST /register`
- `GET /` w `app/web/home.py` renderuje `auth/landing.html`.

## Zmiana 2 — Layout po zalogowaniu

### Wymaganie

- `Wyloguj` w lewym górnym rogu.
- Książki + dodaj książkę na środku lub po lewej.

### Aktualny layout

- `templates/base.html`:
  - header: logo + logout (logout jest po prawej)
  - main: sidebar (z książkami) + content

### Proponowana implementacja

MVP:

- W `templates/base.html`:
  - przenieść formularz `Wyloguj` do lewej części header (obok logo)
  - sidebar zostaje, bo już spełnia „po lewej lista książek + dodaj książkę”

Dodatkowo:

- Po zalogowaniu (POST /login i POST /register) zmienić redirect z `/` na `/books`.
  - Dzięki temu użytkownik od razu widzi listę książek.

## Zmiana 3 — BUG: edycja notatki nie działa

### Objaw

- Kliknięcie „Edytuj” nie przełącza notatki w tryb edycji.
- Użytkownik widzi nadal formularz dodania notatki i ma wrażenie, że edycja dodaje nową.

### Najbardziej prawdopodobna przyczyna (konkret)

W `app/web/books.py` w `books_detail` przekazujemy:

- `edit_note_id = request.query_params.get("edit_note_id")`

To jest **string**.

W `templates/partials/_note_card.html` warunek jest:

- `{% if edit_note_id and edit_note_id == note.id %}`

`note.id` jest UUID (obiekt), więc porównanie `str` vs `UUID` zawsze jest false → edycja nie wchodzi w tryb.

### Fix (MVP)

Jedno z poniższych:

- W `books_detail` przekazywać `edit_note_id` jako UUID (jeśli da się sparsować) albo jako string `str(note.id)`.
- W template porównywać stringi:
  - `edit_note_id == (note.id | string)`

### Weryfikacja

- Klik „Edytuj” na notatce #N → renderuje się `<form method="post" action="/notes/{note_id}">` zamiast view-only.
- Submit edycji aktualizuje notatkę i wraca na `/books/{book_id}`.

## Dodatkowy wymóg bezpieczeństwa (ważne)

Nie commitujemy kluczy:

- Nie dodawać `OPENROUTER_API_KEY=...` do żadnych plików w repo (również `.ai/.dev/commands.txt`).
- W dokumentach zostawić placeholder:
  - `$env:OPENROUTER_API_KEY="..."`

## Checklist wdrożenia (kolejność)

1) Root landing: zaktualizować `home.html` lub dodać `auth/landing.html` + zmienić `GET /`.
2) Redirect po login/register -> `/books`.
3) Layout: `Wyloguj` w lewym górnym rogu.
4) Fix edycji notatek (typ `edit_note_id`).
5) Smoke test:
   - `/` → login/register na środku
   - login → `/books`
   - `/books/{id}` → edycja notatki działa
