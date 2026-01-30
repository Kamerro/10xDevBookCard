# Plan implementacji — POST /auth/register (MVP)

## Cel

Zarejestrować użytkownika (email + hasło) i zwrócić podstawowe dane użytkownika.

## Kontrakt (z `.windsurf/rules/api-plan.md`)

### Request

- `email: EmailStr`
- `password: str`

### Response (200)

- `id: UUID`
- `email: EmailStr`

### Błędy

- `400` jeśli email zajęty lub hasło nie spełnia minimalnych wymagań

## Warstwy i odpowiedzialności (zgodnie z rules)

- `app/api`: HTTP + walidacja + DI, bez logiki biznesowej.
- `app/services`: logika rejestracji (sprawdzenie unikalności email, hash hasła, zapis).
- `app/models`: mapowania SQLAlchemy.

## Kroki implementacji (high-level)

### 1) Modele i DB

- Dodać model `User` w `app/models/user.py`:
  - kolumny zgodne z `.windsurf/rules/db-plan.md`.
  - `id: UUID` jako PK.
  - `email` unikalny.
  - `password_hash`.
  - pola resetu hasła (nullable).
  - `created_at`.

### 2) Schematy Pydantic (API contracts)

- Dodać `app/api/schemas/auth.py`:
  - `RegisterRequest`
  - `UserOut`

### 3) Serwis rejestracji

- Dodać `app/services/auth_service.py`:
  - `create_user(db: Session, email: str, password: str) -> User`
  - Walidacja:
    - email unikalny (zapytanie do DB)
    - minimalne wymagania hasła (MVP: np. `len(password) >= 8`)
  - Hash:
    - bcrypt (zależność z tech-stack)
  - Zapis:
    - `db.add(user)`
    - `db.commit()`
    - `db.refresh(user)`

### 4) Endpoint FastAPI

- W `app/api/auth.py` dodać endpoint `POST /auth/register`:
  - dependency: `db: Session = Depends(get_db)`
  - wywołanie serwisu
  - mapowanie ORM -> Pydantic `UserOut`

## Obsługa błędów

- Email zajęty:
  - `HTTPException(status_code=400, detail="Email already registered")`
- Hasło zbyt krótkie:
  - `HTTPException(status_code=400, detail="Password too short")`
- Błędy DB:
  - nie łapać wyjątków, chyba że chcemy zamienić błąd unique constraint na 400 (opcjonalnie).

## Testy (minimalne, później)

- `pytest`: rejestracja nowego usera zwraca 200.
- Rejestracja z tym samym emailem zwraca 400.

## Workflow 3×3 (proponowana iteracja)

### Iteracja 1 (3 kroki)

1. Dodać model `User` + re-export w `app/models/__init__.py` (jeśli potrzebne).
2. Dodać `RegisterRequest` i `UserOut`.
3. Dodać szkic `auth_service.create_user` (bez maila resetowego).

### Iteracja 2 (3 kroki)

1. Dodać endpoint `POST /auth/register`.
2. Dodać walidację hasła + błąd 400.
3. Dodać sprawdzanie unikalności email.

### Iteracja 3 (3 kroki)

1. Dodać minimalne testy.
2. Dodać migrację Alembic.
3. Wygenerować `curl` do testu manualnego.
