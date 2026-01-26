# Szczegółowy plan implementacji widoku — Books (SSR) (MVP)

## Cel widoku

Zaimplementować główny widok aplikacji w SSR (Jinja2):

- layout 2-kolumnowy
- lista książek po lewej
- szczegóły książki po prawej (gdy wybrana)
- dodawanie notatki (formularz nad fiszkami)
- fiszki notatek + inline edycja bez JS
- badge `processing` na liście książek

Zakres zgodny z `.windsurf/rules/ui-plan.md`.

---

## Wejścia / wyjścia (routing SSR)

### 1) `GET /books`

- Renderuje layout.
- Lewa kolumna: lista książek.
- Prawa kolumna: pusty stan („Wybierz książkę z listy”).

### 2) `GET /books/{book_id}`

- Renderuje layout.
- Lewa kolumna: lista książek, z aktywną pozycją dla `book_id`.
- Prawa kolumna: szczegóły książki + formularz dodania notatki + fiszki.
- Obsługuje query param:
  - `edit_note_id` (UUID) — włącza tryb inline edycji dla jednej fiszki.

### 3) `POST /books/{book_id}/notes`

- Obsługa formularza dodania notatki.
- Po sukcesie redirect do `GET /books/{book_id}`.
- Walidacja: `content` niepuste.

### 4) `POST /notes/{note_id}`

- Obsługa formularza inline edycji notatki.
- Po sukcesie redirect do `GET /books/{book_id}`.
- Walidacja: `content` niepuste.

---

## Integracje danych (kontrakty)

Źródłem danych są serwisy backendowe (warstwa `app/services`) i modele SQLAlchemy:

- `GET /books` wymaga:
  - `books[]`: `id`, `title`, `author`, `ai_status` (badge tylko gdy `processing`)
- `GET /books/{book_id}` wymaga:
  - `book`: `id`, `title`, `author`
  - `notes[]`: `id`, `number`, `content`

Uwaga: to jest SSR, więc kontrolery widoków (routes) powinny wywoływać serwisy bezpośrednio, a nie robić HTTP do własnego API.

---

## Struktura plików (propozycja minimalna)

### Templates

- `templates/base.html`
  - header
  - wrapper layout
  - block content

- `templates/books/index.html`
  - lewa kolumna: lista książek
  - prawa: pusty stan

- `templates/books/detail.html`
  - lewa kolumna: lista książek
  - prawa: szczegóły + formularz + fiszki

- `templates/partials/_book_list.html`
  - render listy książek

- `templates/partials/_note_card.html`
  - render fiszki
  - wariant: normal / edit-mode

### Static

- `static/styles.css`
  - minimalne style layoutu, card, badge, button, input

### Python (routing widoków)

- `app/web/router.py`
- `app/web/books.py`

---

## Layout i komponenty UI

### Header

- logo/nazwa aplikacji (link do `/books`)
- placeholder: `Wyloguj`

### Kolumny

- lewa: stała szerokość (np. 320px), scroll jeśli dużo książek
- prawa: elastyczna

### Lista książek (lewa)

Element listy:

- tytuł
- autor
- badge `processing` tylko jeśli `ai_status == "processing"`
- stan aktywny (dla `/books/{book_id}`)

### Szczegóły książki (prawa)

- nagłówek: title + author
- formularz dodania notatki: `textarea` + button
- lista notatek: karty

### Fiszka notatki

- header: `Note #{number}`
- body: `content` (pełny)
- akcje:
  - „Edytuj” (link do `?edit_note_id=...`)

### Inline edit mode

Dla notatki o `id == edit_note_id`:

- zamiast contentu renderujemy `textarea` + „Zapisz” + „Anuluj”
- submit idzie do `POST /notes/{note_id}`

---

## Walidacja i błędy (MVP)

- Dodanie notatki:
  - jeśli `content` puste: pokaż błąd pod formularzem, bez utraty reszty widoku
- Edycja notatki:
  - jeśli `content` puste: pokaż błąd w fiszce edytowanej
- 404 / brak dostępu:
  - dla `book_id`/`note_id` nie należących do usera: prosty komunikat (może być w prawym panelu)

---

## Plan implementacji (workflow 3×3)

### Iteracja 1 (3 kroki)

1. Dodać routing dla widoków SSR: `GET /books` i `GET /books/{book_id}` (szkielety).
2. Dodać minimalne templaty: `base.html`, `books/index.html`, `books/detail.html` (bez stylowania).
3. Dodać partiale `_book_list.html` i `_note_card.html` (wersja tylko read-only).

### Iteracja 2 (3 kroki)

1. Dodać formularz dodania notatki w `detail.html` + route `POST /books/{book_id}/notes`.
2. Dodać inline edit mode (param `edit_note_id`) + route `POST /notes/{note_id}`.
3. Dodać walidację contentu i komunikaty błędów w templatach.

### Iteracja 3 (3 kroki)

1. Dodać minimalistyczne CSS (layout, card, badge, button, input).
2. Dodać badge `processing` w liście książek.
3. Dodać szybkie testy manualne (opis kroków + przykładowe requesty), ewentualnie minimalny test renderowania widoku.

---

## Checkpoint / status pliku

Jeśli przerwiemy pracę w połowie wdrożenia, tworzymy plik statusu widoku (wg lekcji):

- `.ai/books-view-implementation-status.md`
