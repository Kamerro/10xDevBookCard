# BookCards — UI plan (MVP)

## Source of truth

- PRD: `.ai/prd.md`
- Tech stack: `.ai/tech-stack.md`
- Rules: `.windsurf/rules/*`

Zakres: MVP, SSR (Jinja2), minimalistyczne CSS, brak SPA i brak frameworków JS.

---

## Cele UI (MVP)

- Ultra prosty layout.
- Minimalna liczba interakcji.
- Kluczowy widok: **widok książki + dodawanie notatek**.
- Notatki prezentowane jako estetyczne „fiszki”.
- Inline edycja notatki bez JS (pełny reload).

---

## Mapa podróży użytkownika (MVP)

1. Użytkownik przechodzi do listy książek.
2. Kliknięcie książki otwiera jej szczegóły po prawej stronie.
3. Użytkownik dodaje notatkę (pojedyncze pole tekstowe) i widzi ją na liście fiszek.
4. Użytkownik edytuje notatkę inline.
5. AI uruchamia się asynchronicznie po dodaniu >= 3 notatek (UI pokazuje status na liście książek).

---

## Layout i nawigacja

### Stały header

- Widoczny na każdej stronie.
- Elementy:
  - Nazwa aplikacji: `BookCards` (link do listy książek)
  - Akcje po prawej: placeholder na `Wyloguj` (MVP auth jest w PRD, ale UI auth może być wdrażane później)

### Layout 2-kolumnowy (lista + szczegóły)

- Lewa kolumna: lista książek.
- Prawa kolumna: szczegóły wybranej książki.
- W stanie początkowym (gdy brak wybranej książki): prawa strona jest pusta i pokazuje krótki komunikat typu „Wybierz książkę z listy”.

---

## Widoki i strony (SSR)

### 1) Lista książek + panel szczegółów (główny widok)

#### URL

- `GET /books`

#### Zachowanie

- Renderuje layout 2-kolumnowy.
- Prawa kolumna jest pusta (brak wybranej książki).

#### Lewa kolumna — lista książek

Każdy element listy:

- Tytuł
- Autor
- Badge statusu AI:
  - wyświetlany **tylko gdy** status == `processing`

Interakcje:

- klik w element listy → `GET /books/{book_id}` (pełny reload)

#### Prawa kolumna — stan pusty

- Tekst: „Wybierz książkę z listy”

---

### 2) Szczegóły książki + notatki (w tym samym layoucie)

#### URL

- `GET /books/{book_id}`

#### Zachowanie

- Renderuje ten sam layout 2-kolumnowy.
- Lewa kolumna nadal pokazuje listę książek.
- Prawa kolumna pokazuje wybraną książkę.

#### Prawa kolumna — sekcje

1. Nagłówek książki:
   - `title`
   - `author`

2. Formularz dodania notatki (nad fiszkami):
   - jedno pole `textarea` lub `input` (preferowane `textarea` dla wygody)
   - przycisk: „Dodaj notatkę”

3. Lista fiszek notatek:
   - Każda fiszka:
     - tytuł: `Note #{number}`
     - content: pełny tekst
     - akcja: „Edytuj”

---

## Inline edycja notatki (bez JS)

### Mechanika

- Klik „Edytuj” na fiszce:
  - prowadzi do `GET /books/{book_id}?edit_note_id={note_id}`

### Renderowanie

- Jeśli `edit_note_id` odpowiada notatce z listy:
  - zamiast widoku contentu fiszki renderujemy formularz edycji:
    - `textarea` z obecną treścią
    - przycisk: „Zapisz”
    - link: „Anuluj” (powrót do `GET /books/{book_id}`)

### Submit

- Submit formularza edycji:
  - `POST /notes/{note_id}` (MVP SSR)
  - po zapisie redirect do `GET /books/{book_id}`

Uwaga:

- API plan przewiduje `PUT /notes/{note_id}` dla REST. Dla SSR możemy zastosować `POST` + redirect, zachowując wewnętrzną logikę identyczną.

---

## Styling (minimalistyczne CSS)

Cele stylistyczne:

- Czytelne typografie i spacing.
- Fiszki z wyraźnym obramowaniem, delikatnym cieniem, zaokrąglonymi rogami.
- Badge `processing` w liście książek (mały, kontrastowy).

Minimalny zestaw komponentów wizualnych (Jinja partials):

- `card` (fiszka)
- `badge` (status)
- `button`
- `input/textarea`

---

## Integracja danych (źródła)

- Lista książek: `GET /books` (backend pobiera books usera i status AI)
- Szczegóły książki: `GET /books/{book_id}` (book + notes + opcjonalnie AI)
- Dodanie notatki: `POST /books/{book_id}/notes`
- Edycja notatki (SSR): `POST /notes/{note_id}`

---

## Obsługa stanów i błędów (MVP)

- Pusta lista książek:
  - komunikat w lewej kolumnie: „Dodaj pierwszą książkę”.
- Brak notatek:
  - komunikat w prawej kolumnie: „Dodaj pierwszą notatkę”.
- Błędy walidacji (np. pusta notatka):
  - proste komunikaty pod formularzem.
- `404` (book/note nie istnieje lub nie należy do usera):
  - prosta strona błędu lub komunikat w layoucie.

---

## Pliki (proponowana struktura)

- `templates/base.html` (header + layout)
- `templates/books/index.html` (GET /books)
- `templates/books/detail.html` (GET /books/{id})
- `templates/partials/_book_list.html`
- `templates/partials/_note_card.html`
- `static/styles.css`

---

## Następny krok

- Przygotować szczegółowy plan implementacji widoku: `books-detail-view-implementation-plan.md`.
- Następnie wdrażać w workflow 3×3.
