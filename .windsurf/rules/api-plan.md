# BookCards — API plan (MVP)

## Source of truth

- PRD: `.ai/prd.md`
- Tech stack: `.ai/tech-stack.md`
- Rules: `.windsurf/rules/*`

Zakres: MVP, REST (JSON), FastAPI + Pydantic v2, SQLAlchemy 2.0, PostgreSQL. Brak Supabase. Bez implementacji logiki biznesowej.

---

## Ogólne zasady API

- Endpointy asynchroniczne (`async def`) w FastAPI.
- API zwraca wyłącznie Pydantic modele lub dicty (nigdy ORM).
- Warstwa `app/api`:
  - tylko HTTP, walidacja, zależności auth/DB
  - brak logiki biznesowej
- Sesja DB przez dependency injection (`get_db`).
- Błędy: jawne `HTTPException`, fail fast.

### Base path (ważne)

- JSON API jest mountowane pod prefixem: **`/api`** (patrz `app/main.py`).
- To rozdziela routing JSON API od SSR (Jinja2), który używa ścieżek typu `/books`.
- W praktyce:
  - `POST /auth/login` w tym dokumencie oznacza **`POST /api/auth/login`**
  - `GET /books` w tym dokumencie oznacza **`GET /api/books`**

---

## Auth (JWT access token)

- JWT access token only (MVP).
- Brak refresh tokenów.
- Hash haseł: bcrypt.
- Reset hasła: token wysyłany emailowo (mechanika wysyłki poza zakresem planu API; API dostarcza endpointy).

### Kontrakt tokena

- Token przekazywany w nagłówku:
  - `Authorization: Bearer <access_token>`

Uwaga:

- SSR UI ustawia token jako cookie `access_token` (dla wygody formularzy i redirectów).
- JSON API nadal używa nagłówka `Authorization: Bearer ...`.

---

## Zasoby i endpointy

Poniżej opis endpointów wymaganych przez PRD.

### 1) Auth

#### POST `/auth/register`

- **Opis**: rejestracja użytkownika (email + hasło).
- **Auth**: brak.

Request (Pydantic)

- `email: EmailStr`
- `password: str`

Response

- `id: UUID`
- `email: EmailStr`

Błędy

- `400` jeśli email zajęty lub hasło nie spełnia minimalnych wymagań

---

#### POST `/auth/login`

- **Opis**: logowanie, zwraca JWT access token.
- **Auth**: brak.

Request

- `email: EmailStr`
- `password: str`

Response

- `access_token: str`
- `token_type: Literal["bearer"]` (wartość stała: `bearer`)

Błędy

- `401` jeśli błędne dane logowania

---

#### POST `/auth/password-reset/request`

- **Opis**: żądanie resetu hasła (wysyłka tokenu na email).
- **Auth**: brak.

Request

- `email: EmailStr`

Response

- `{ "ok": true }`

Błędy

- `200` zawsze (nie ujawniamy czy email istnieje)

---

#### POST `/auth/password-reset/confirm`

- **Opis**: ustawienie nowego hasła na podstawie tokenu.
- **Auth**: brak.

Request

- `token: str`
- `new_password: str`

Response

- `{ "ok": true }`

Błędy

- `400` jeśli token niepoprawny / wygasł

---

### 2) Books

#### POST `/books`

- **Opis**: dodanie książki (minimum: tytuł, autor).
- **Auth**: wymagany.

Request

- `title: str`
- `author: str`

Response

- `id: UUID`
- `title: str`
- `author: str`
- `created_at: datetime`

Błędy

- `401` brak/niepoprawny token

---

#### GET `/books`

- **Opis**: lista książek zalogowanego użytkownika.
- **Auth**: wymagany.

Response

Lista elementów:

- `id: UUID`
- `title: str`
- `author: str`
- `created_at: datetime`
- `ai_status: str` (np. `pending|processing|done|failed`)

Uwagi

- Jeśli rekord analizy AI (1:1) jeszcze nie istnieje dla książki, `ai_status` zwracamy jako `pending`.

Błędy

- `401` brak/niepoprawny token

---

#### DELETE `/books/{book_id}`

- **Opis**: usuwa książkę wraz z notatkami.
- **Auth**: wymagany.

Path

- `book_id: UUID`

Response

- `{ "ok": true }`

Błędy

- `401` brak/niepoprawny token
- `404` jeśli książka nie należy do usera lub nie istnieje

---

#### GET `/books/{book_id}`

- **Opis**: szczegóły książki + notatki + (opcjonalnie) wynik AI.
- **Auth**: wymagany.

Path

- `book_id: UUID`

Response

- `id: UUID`
- `title: str`
- `author: str`
- `created_at: datetime`
- `notes: list[NoteOut]`
- `ai: BookAIAnalysisOut | None`

Błędy

- `401` brak/niepoprawny token
- `404` jeśli książka nie należy do usera lub nie istnieje

---

### 3) Notes

#### POST `/books/{book_id}/notes`

- **Opis**: dodanie pojedynczej notatki do książki.
- **Auth**: wymagany.

Path

- `book_id: UUID`

Request

- `content: str`

Response

- `id: UUID`
- `book_id: UUID`
- `number: int`
- `content: str`
- `created_at: datetime`
- `updated_at: datetime`

Błędy

- `401` brak/niepoprawny token
- `404` jeśli książka nie należy do usera lub nie istnieje

Uwagi

- Po dodaniu notatki, jeśli książka ma >= 3 notatki, należy uruchomić background task AI (poza warstwą API).
- MVP rekomendacja dla spójności UI:
  - jeśli analiza jeszcze nie istnieje, utworzyć rekord 1:1 dla książki ze statusem `pending` lub `processing`
  - po starcie zadania ustawić `processing`
  - po zakończeniu: `done` i zapisać wyniki
  - w przypadku błędu: `failed` + `analysis_error`

---

#### PUT `/notes/{note_id}`

- **Opis**: edycja (nadpisanie) notatki po `note_id`.
- **Auth**: wymagany.

Path

- `note_id: UUID`

Request

- `content: str`

Response

- `id: UUID`
- `book_id: UUID`
- `number: int`
- `content: str`
- `created_at: datetime`
- `updated_at: datetime`

Błędy

- `401` brak/niepoprawny token
- `404` jeśli notatka nie należy do usera lub nie istnieje

---

## Kontrakty (Pydantic — propozycja modułów)

Prosty podział (bez nadmiarowych abstrakcji):

- `app/api/schemas/auth.py`
- `app/api/schemas/books.py`
- `app/api/schemas/notes.py`

### Typy współdzielone

- `UUID` z `uuid`.
- Daty: `datetime` (z timezone), serializowane przez FastAPI.

---

## Autoryzacja i zależności

### Dependency: aktualny użytkownik

- `get_current_user` (plan)
  - odczyt `Authorization` header
  - weryfikacja JWT
  - pobranie usera z DB

W API planie to jest dependency wykorzystywane przez endpointy books/notes.

---

## Kody błędów (wspólne)

- `400` — walidacja inputu / niepoprawne dane
- `401` — brak/niepoprawny JWT
- `404` — zasób nie istnieje lub nie należy do usera
- `500` — błąd serwera (nie łapiemy wyjątków bez potrzeby)

---

## Testowanie (MVP)

- Szybkie testy manualne przez `curl`.
- Minimalne testy automatyczne w `pytest` (w kolejnym kroku, poza tym dokumentem).
