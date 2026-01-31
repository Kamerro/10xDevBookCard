# Test Plan — BookCards (MVP) — TDD

## Cel

Ten dokument jest **planem testów** do wdrożenia w sposób **TDD** (najpierw testy, potem implementacja/refactor). Plan obejmuje:

- SSR UI (Jinja2) — routing, redirecty, walidacja formularzy
- JSON API (FastAPI) pod prefixem **`/api`** — status codes i kontrakty

Dokument jest napisany tak, aby inny model mógł go bezpośrednio wdrażać.

---

## Source of truth

- `.ai/prd.md`
- `.ai/tech-stack.md`
- Kod:
  - `app/main.py` (mount `/api`)
  - `app/web/auth.py`, `app/web/books.py`
  - `app/api/auth.py`, `app/api/books.py`, `app/api/notes.py`

---

## Założenia (obecny stan aplikacji)

### Routing

- **SSR (HTML)** bez prefixu:
  - `/` (public)
  - `/login`, `/register`, `/forgot-password` (public)
  - `/logout` (POST)
  - `/books`, `/books/{book_id}` (chronione)
  - `/books/{book_id}/notes` (POST, chronione)
  - `/notes/{note_id}` (POST, chronione)

- **JSON API** pod prefixem `/api`:
  - `/api/auth/register` (POST)
  - `/api/auth/login` (POST)
  - `/api/books` (POST, GET)
  - `/api/books/{book_id}` (GET, DELETE)
  - `/api/books/{book_id}/notes` (POST)
  - `/api/notes/{note_id}` (PUT)
  - `/api/health` (GET) — jeśli istnieje

### Auth (JWT)

- SSR:
  - sesja: cookie `access_token` (HttpOnly)
  - brak cookie → redirect `303` do `/login`

- JSON API:
  - auth przez `Authorization: Bearer <token>`
  - brak/niepoprawny/expired token → `401`

### Błędy SSR

SSR w wielu przypadkach preferuje **redirect** zamiast `404` HTML (stan aktualny kodu):

- nieprawidłowy UUID w path → `303` do `/books`
- zasób nie istnieje / nie należy do usera → `303` do `/books`

### AI

- Trigger AI po >= 3 notatkach jest **docelowy** i **nie jest częścią tego planu testów endpointów** (chyba że osobno dopiszesz plan dla AI).

---

## Środowisko testowe

### Framework

- `pytest`

### Styl TDD

- Każdy endpoint / przypadek:
  - najpierw test (z oczekiwanym statusem i body/redirect)
  - potem implementacja lub refactor

### DB

- Preferowane: osobna baza testowa Postgres.
- Jeśli używasz SQLite in-memory: pamiętaj o typach Postgres (np. JSONB) — testy mogą wymagać patchowania typów lub użycia Postgres.

### Klient testowy

- FastAPI `TestClient`.

---

## Konwencje w testach

### Dane testowe

- **User A** i **User B**.
- Książki należące do User A.
- Notatki należące do książki User A.

### Helpers / Fixtures (propozycja)

- `client` — TestClient
- `db_session` — transakcyjna sesja testowa
- `user_a`, `user_b`
- `token_a`, `token_b` (JWT)
- `auth_header_a = {"Authorization": f"Bearer {token_a}"}`
- `book_a1` (book user_a)
- `note_a1` (note for book_a1)

---

# Testy — JSON API (`/api/*`)

## 1) Auth API

### 1.1 POST `/api/auth/register`

- **TC-AUTH-REG-001**
  - **Given**: payload `{email, password}` (+ opcjonalnie `password_confirm`)
  - **When**: POST `/api/auth/register`
  - **Then**: `200`
  - **And**: response zawiera `id`, `email`

- **TC-AUTH-REG-002**
  - **Given**: email zajęty
  - **When**: POST `/api/auth/register`
  - **Then**: `400`

- **TC-AUTH-REG-003**
  - **Given**: `password_confirm != password`
  - **When**: POST `/api/auth/register`
  - **Then**: `400`

- **TC-AUTH-REG-004**
  - **Given**: hasło nie spełnia reguł (długość / uppercase / digit / special)
  - **When**: POST `/api/auth/register`
  - **Then**: `400`

### 1.2 POST `/api/auth/login`

- **TC-AUTH-LOGIN-001**
  - **Given**: poprawny user
  - **When**: POST `/api/auth/login`
  - **Then**: `200`
  - **And**: response zawiera `access_token` (str) i `token_type == "bearer"`

- **TC-AUTH-LOGIN-002**
  - **Given**: błędne hasło
  - **When**: POST `/api/auth/login`
  - **Then**: `401`

---

## 2) Books API

### 2.1 POST `/api/books`

- **TC-API-BOOKS-CREATE-001**
  - **Given**: auth header A
  - **When**: POST `/api/books` z `{title, author}`
  - **Then**: `201`
  - **And**: response zawiera `id`, `created_at`
  - **And**: book zapisany w DB z `user_id == user_a.id`

- **TC-API-BOOKS-CREATE-002**
  - **Given**: brak Bearer token
  - **When**: POST `/api/books`
  - **Then**: `401`

### 2.2 GET `/api/books`

- **TC-API-BOOKS-LIST-001**
  - **Given**: User A ma N książek
  - **When**: GET `/api/books` z auth A
  - **Then**: `200`
  - **And**: lista zawiera tylko książki user A

- **TC-API-BOOKS-LIST-002**
  - **Given**: auth B
  - **When**: GET `/api/books`
  - **Then**: `200`
  - **And**: lista nie zawiera książek user A

### 2.3 GET `/api/books/{book_id}`

- **TC-API-BOOKS-DETAIL-001**
  - **Given**: book należy do user A
  - **When**: GET `/api/books/{book_id}` z auth A
  - **Then**: `200`
  - **And**: response zawiera `notes` jako listę (posortowaną po `number`)

- **TC-API-BOOKS-DETAIL-002**
  - **Given**: book należy do user A
  - **When**: GET `/api/books/{book_id}` z auth B
  - **Then**: `404` ("Book not found")

- **TC-API-BOOKS-DETAIL-003**
  - **Given**: book_id nie istnieje
  - **When**: GET `/api/books/{book_id}`
  - **Then**: `404`

### 2.4 DELETE `/api/books/{book_id}`

- **TC-API-BOOKS-DELETE-001**
  - **Given**: book należy do user A i ma notatki
  - **When**: DELETE `/api/books/{book_id}` z auth A
  - **Then**: `200` + body `{ok: true}`
  - **And**: book usunięty
  - **And**: notatki usunięte kaskadowo

- **TC-API-BOOKS-DELETE-002**
  - **Given**: book należy do user A
  - **When**: DELETE `/api/books/{book_id}` z auth B
  - **Then**: `404`

---

## 3) Notes API

### 3.1 POST `/api/books/{book_id}/notes`

- **TC-API-NOTES-CREATE-001**
  - **Given**: book należy do user A
  - **When**: POST `/api/books/{book_id}/notes` z auth A i `{content}`
  - **Then**: `201`
  - **And**: `number` rośnie per book (1,2,3...)

- **TC-API-NOTES-CREATE-002**
  - **Given**: book należy do user A
  - **When**: POST `/api/books/{book_id}/notes` z auth B
  - **Then**: `404` ("Book not found")

- **TC-API-NOTES-CREATE-003**
  - **Given**: brak auth
  - **When**: POST `/api/books/{book_id}/notes`
  - **Then**: `401`

### 3.2 PUT `/api/notes/{note_id}`

- **TC-API-NOTES-UPDATE-001**
  - **Given**: note należy do user A
  - **When**: PUT `/api/notes/{note_id}` z auth A i `{content}`
  - **Then**: `200`
  - **And**: `updated_at` ulega zmianie

- **TC-API-NOTES-UPDATE-002**
  - **Given**: note należy do user A
  - **When**: PUT `/api/notes/{note_id}` z auth B
  - **Then**: `404` ("Note not found")

- **TC-API-NOTES-UPDATE-003**
  - **Given**: brak auth
  - **When**: PUT `/api/notes/{note_id}`
  - **Then**: `401`

---

## 4) Health API

- **TC-API-HEALTH-001**
  - **When**: GET `/api/health`
  - **Then**: `200`

---

# Testy — SSR (HTML)

## 1) Public pages

### 1.1 GET `/login`

- **TC-SSR-LOGIN-PAGE-001**
  - **When**: GET `/login`
  - **Then**: `200`

### 1.2 POST `/login`

- **TC-SSR-LOGIN-001**
  - **Given**: poprawne dane
  - **When**: POST `/login`
  - **Then**: `303`
  - **And**: response ma cookie `access_token`
  - **And**: `Location: /`

- **TC-SSR-LOGIN-002**
  - **Given**: błędne dane
  - **When**: POST `/login`
  - **Then**: `200` (render HTML)
  - **And**: w HTML jest komunikat błędu (`error_login`)

### 1.3 GET `/register`

- **TC-SSR-REGISTER-PAGE-001**
  - **When**: GET `/register`
  - **Then**: `200`

### 1.4 POST `/register`

- **TC-SSR-REGISTER-001**
  - **Given**: password_confirm == password
  - **When**: POST `/register`
  - **Then**: `303`
  - **And**: cookie `access_token` ustawione

- **TC-SSR-REGISTER-002**
  - **Given**: password_confirm != password
  - **When**: POST `/register`
  - **Then**: `200` (render HTML)
  - **And**: błąd w HTML (`error_register`)

### 1.5 POST `/logout`

- **TC-SSR-LOGOUT-001**
  - **Given**: client ma cookie `access_token`
  - **When**: POST `/logout`
  - **Then**: `303`
  - **And**: cookie `access_token` usunięte

---

## 2) Protected SSR pages (wymagają cookie)

### 2.1 GET `/books`

- **TC-SSR-BOOKS-INDEX-001**
  - **Given**: brak cookie
  - **When**: GET `/books`
  - **Then**: `303` do `/login`

- **TC-SSR-BOOKS-INDEX-002**
  - **Given**: cookie user A
  - **When**: GET `/books`
  - **Then**: `200`
  - **And**: HTML renderuje listę książek

### 2.2 GET `/books/{book_id}`

- **TC-SSR-BOOKS-DETAIL-001**
  - **Given**: brak cookie
  - **When**: GET `/books/{book_id}`
  - **Then**: `303` do `/login`

- **TC-SSR-BOOKS-DETAIL-002**
  - **Given**: cookie user A i book A
  - **When**: GET `/books/{book_id}`
  - **Then**: `200`

- **TC-SSR-BOOKS-DETAIL-003**
  - **Given**: cookie user A
  - **When**: GET `/books/{invalid_uuid}`
  - **Then**: `303` do `/books`

- **TC-SSR-BOOKS-DETAIL-004**
  - **Given**: cookie user A
  - **When**: GET `/books/{book_of_user_b}`
  - **Then**: `303` do `/books`

---

## 3) SSR actions

### 3.1 POST `/books` (create book)

- **TC-SSR-BOOKS-CREATE-001**
  - **Given**: brak cookie
  - **When**: POST `/books`
  - **Then**: `303` do `/login`

- **TC-SSR-BOOKS-CREATE-002**
  - **Given**: cookie user A
  - **When**: POST `/books` z pustym `title` lub `author`
  - **Then**: `200` (render index)
  - **And**: `error_add_book` w HTML

- **TC-SSR-BOOKS-CREATE-003**
  - **Given**: cookie user A
  - **When**: POST `/books` z poprawnym payload
  - **Then**: `303` do `/books`
  - **And**: book zapisany w DB

### 3.2 POST `/books/{book_id}/notes` (create note)

- **TC-SSR-NOTES-CREATE-001**
  - **Given**: brak cookie
  - **When**: POST `/books/{book_id}/notes`
  - **Then**: `303` do `/login`

- **TC-SSR-NOTES-CREATE-002**
  - **Given**: cookie user A i book A
  - **When**: POST `/books/{book_id}/notes` z pustym content
  - **Then**: `200` (render detail)
  - **And**: `error_add_note` w HTML

- **TC-SSR-NOTES-CREATE-003**
  - **Given**: cookie user A i book A
  - **When**: POST `/books/{book_id}/notes` z poprawnym content
  - **Then**: `303` do `/books/{book_id}`
  - **And**: note zapisana w DB

- **TC-SSR-NOTES-CREATE-004**
  - **Given**: cookie user A
  - **When**: POST `/books/{book_of_user_b}/notes`
  - **Then**: `303` do `/books`

### 3.3 POST `/notes/{note_id}` (update note)

- **TC-SSR-NOTES-UPDATE-001**
  - **Given**: brak cookie
  - **When**: POST `/notes/{note_id}`
  - **Then**: `303` do `/login`

- **TC-SSR-NOTES-UPDATE-002**
  - **Given**: cookie user A, note A, brak `book_id` w form
  - **When**: POST `/notes/{note_id}`
  - **Then**: `303` do `/books`

- **TC-SSR-NOTES-UPDATE-003**
  - **Given**: cookie user A, note A
  - **When**: POST `/notes/{note_id}` z pustym content
  - **Then**: `200` (render detail)
  - **And**: `error_edit_note` w HTML

- **TC-SSR-NOTES-UPDATE-004**
  - **Given**: cookie user A, note A
  - **When**: POST `/notes/{note_id}` z poprawnym content
  - **Then**: `303` do `/books/{book_id}`
  - **And**: note zaktualizowana w DB

- **TC-SSR-NOTES-UPDATE-005**
  - **Given**: cookie user A
  - **When**: POST `/notes/{note_of_user_b}`
  - **Then**: `303` do `/books/{book_id}` (lub `/books` jeśli brak book) — zgodnie z aktualnym kodem

---

## Checklist: regresja konfliktu routingu

- **TC-ROUTING-CONFLICT-001**
  - **When**: zalogowany user w SSR wchodzi w `/books`
  - **Then**: dostaje SSR (HTML) `200` (nie `401`)
  - **And**: endpointy API są dostępne tylko pod `/api/*`

---

## Notatki implementacyjne (dla modelu wdrażającego)

- Testy SSR będą wymagały obsługi cookies w `TestClient`.
- Testy API będą wymagały generacji JWT albo wywołania `/api/auth/login`.
- Jeżeli testy na SQLite sprawiają problemy przez typy Postgres, przenieś testy na Postgres test DB.
