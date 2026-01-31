# Env Config — BookCards

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](./GOVERNANCE.md)
> - [PRD](./prd.md)

## Cel

Jedno miejsce, które opisuje **zmienne środowiskowe**, ich przeznaczenie oraz wymagania dla:

- dev
- CI
- prod

## Zasady

- Sekrety nigdy nie trafiają do repo.
- W repo utrzymujemy tylko `.env.example` z placeholderami.

## Zmienne (wymagane / typowe)

### A) Aplikacja

- `DATABASE_URL`
  - **dev/prod:** Postgres URL
  - **CI:** dopuszczalne sqlite, np. `sqlite:///./test.db`

- `JWT_SECRET_KEY` (albo `JWT_SECRET` — utrzymaj spójność nazw w kodzie)
  - secret do podpisu JWT

- `JWT_ALGORITHM`
  - domyślnie `HS256`

### B) AI (OpenRouter)

- `OPENROUTER_API_KEY` (required dla AI)
- `OPENROUTER_MODEL` (opcjonalne)
- `OPENROUTER_BASE_URL` (opcjonalne)
- `OPENROUTER_TIMEOUT_SECONDS` (opcjonalne)

## Minimalne konfiguracje

### Dev (przykład)

- `DATABASE_URL=postgresql+psycopg://...`
- `JWT_SECRET_KEY=...`
- `OPENROUTER_API_KEY=...` (jeśli testujesz AI)

### CI (przykład)

- `DATABASE_URL=sqlite:///./test.db`
- `JWT_SECRET_KEY=test-secret-key-for-ci`
- bez `OPENROUTER_API_KEY` (testy mają działać bez realnych calli)

### Prod (przykład)

- `DATABASE_URL=postgresql+psycopg://...`
- `JWT_SECRET_KEY=...`
- `OPENROUTER_API_KEY=...`

## Uwaga o `.env`

- Sam plik `.env` nie jest automatycznie ładowany przez Pythona.
- Jeśli chcesz wspierać `.env`, dodaj jawne ładowanie (np. `python-dotenv`) i opisz to w GOVERNANCE.
