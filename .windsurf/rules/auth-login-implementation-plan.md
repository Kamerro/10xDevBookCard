# Plan implementacji — POST /auth/login (MVP)

## Cel

Zalogować użytkownika i zwrócić JWT access token.

## Kontrakt (z `.windsurf/rules/api-plan.md`)

### Request

- `email: EmailStr`
- `password: str`

### Response (200)

- `access_token: str`
- `token_type: "bearer"`

### Błędy

- `401` jeśli błędne dane logowania

## Warstwy

- `app/api`: HTTP + DI.
- `app/services`: weryfikacja hasła + generowanie tokena.
- `app/core`: konfiguracja JWT secret/alg/exp (settings/env).

## Kroki implementacji (high-level)

### 1) Konfiguracja JWT

- Rozszerzyć `app/core/settings.py` o:
  - `jwt_secret_key`
  - `jwt_algorithm` (np. `HS256`)
  - `jwt_access_token_exp_minutes`

### 2) Serwis auth

- W `app/services/auth_service.py`:
  - `authenticate_user(db: Session, email: str, password: str) -> User | None`
    - pobierz usera po email
    - `bcrypt.checkpw`
  - `create_access_token(user_id: UUID) -> str`
    - wygeneruj JWT z `sub=user_id`
    - `exp` wg ustawień

### 3) Schematy Pydantic

- `LoginRequest`
- `TokenOut`

### 4) Endpoint

- `POST /auth/login` w `app/api/auth.py`:
  - jeśli auth fail -> `HTTPException(401)`
  - else -> `TokenOut(access_token=..., token_type="bearer")`

## Obsługa błędów

- zawsze `401` przy błędnym email/haśle (bez ujawniania szczegółów)

## Testy (minimalne, później)

- logowanie poprawne -> 200 + token
- logowanie błędne -> 401

## Workflow 3×3 (proponowana iteracja)

### Iteracja 1 (3 kroki)

1. Dodać settings JWT.
2. Dodać funkcje `authenticate_user` i `create_access_token`.
3. Dodać Pydantic schematy `LoginRequest` i `TokenOut`.

### Iteracja 2 (3 kroki)

1. Dodać endpoint `POST /auth/login`.
2. Dodać minimalne testy.
3. Dodać przykładowy `curl` do manualnego testu.
