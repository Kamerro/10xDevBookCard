# E2E Tests — BookCards

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](./GOVERNANCE.md)
> - [PRD](./prd.md)

## Cel

Ten dokument opisuje jak mają przebiegać testy E2E dla BookCards:

- co testujemy (scope)
- jakie flow są krytyczne
- jak przygotowujemy dane
- jak uruchamiamy lokalnie
- jak później wpinamy w CI/CD

Na ten etap to **specyfikacja/proces** — implementacja frameworka E2E może być w kolejnym kroku.

## Status w repo

- Testy E2E są trzymane w: `tests/e2e/`
- Konfiguracja Playwright: `playwright.config.ts`
- Workflow w GitHub Actions (manual): `.github/workflows/e2e.yml`

## Wybór narzędzia (rekomendacja)

- **Playwright** (preferowane)
  - stabilny, szybki, dobre debugowanie
  - można testować UI SSR bez przebudowy frontu

## Zasady ogólne

- Testy E2E weryfikują zachowanie z perspektywy użytkownika, nie implementację.
- Testy muszą być deterministyczne:
  - bez losowych sleepów
  - używamy waitów na elementy / response
- E2E nie może zależeć od realnego OpenRouter.
  - AI powinno być mockowane / wyłączone w trybie E2E

## Środowiska

### Lokalnie

- uruchamiasz aplikację lokalnie (`uvicorn ...`) lub przez skrypt `make`/`python -m ...` (jeśli dodamy)
- baza danych może być:
  - sqlite w pliku (na start)
  - albo Postgres lokalnie (później)

### CI (później)

- E2E są uruchamiane w osobnym workflow `e2e.yml`.
- Na start workflow jest **manual** (`workflow_dispatch`).

## OpenRouter connectivity check (w CI)

- Workflow `e2e.yml` wykonuje dodatkowo check połączenia do OpenRouter.
- Wymagany jest GitHub Secret:
  - `OPENROUTER_API_KEY`

## Dane testowe

### Zasada

Każdy test powinien działać na **świeżych danych**.

### Opcje podejścia (wybierz jedno)

1) **Seed przez API** (preferowane)
- test robi register/login i buduje dane przez UI/API

2) **Seed przez DB** (później)
- szybciej, ale więcej coupling do modelu

### Cleanup

- testy nie mogą “brudzić” danych między runami
- preferowane: osobna baza na run (np. `test-e2e.db`)

## Krytyczne scenariusze E2E (MVP)

### 1) Public landing

- Wejście na `/`
- Widzisz CTA: Logowanie / Rejestracja

### 2) Rejestracja + login

- `GET /register` -> render
- `POST /register` poprawny -> redirect do `/books`
- `POST /login` poprawny -> redirect do `/books`
- błędny login -> komunikat błędu

### 3) Książki: create + list

- Na `/books` widać:
  - listę książek
  - formularz dodania książki
- Dodanie książki -> pojawia się na liście

### 4) Notatki: create + edit

- Wejście w `/books/{id}`
- Dodanie notatki -> pojawia się na stronie
- Klik “Edytuj” na notatce -> pojawia się formularz edycji
- Zapis edycji -> treść notatki się aktualizuje (nie tworzy nowej)

### 5) Logout

- Klik `Wyloguj`
- Próba wejścia na `/books` bez sesji -> redirect do `/login` (lub landing)

## Selektory / stabilność UI

Żeby E2E było stabilne, docelowo dodamy `data-testid` w krytycznych elementach:

- `data-testid="nav-login"`, `nav-register"
- `data-testid="book-create-form"`
- `data-testid="book-list"`
- `data-testid="note-card"`, `note-edit"`

Na MVP można startować od selektorów tekstowych, ale `data-testid` jest preferowane.

## Konwencje testów

- Struktura (docelowo):
  - `tests/e2e/` (scenariusze)
  - `tests/e2e/pages/` (page objects)

- Nazewnictwo:
  - `auth.spec.ts`
  - `books.spec.ts`
  - `notes.spec.ts`

## Debugowanie

- zawsze zapisuj screenshoty/video przy failu
- w Playwright:
  - trace
  - video

## Integracja z CI (plan)

1) dodać workflow `.github/workflows/e2e.yml` (manual)
2) uruchamiać app w background (na CI) + odpalić Playwright
3) (opcjonalnie) dopiero potem uczynić E2E wymaganym checkiem na `main`
