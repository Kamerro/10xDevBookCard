# Test Strategy — BookCards

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](./GOVERNANCE.md)
> - [PRD](./prd.md)

## Cel

Zdefiniować minimalną strategię testowania dla v1.0 i kierunek pod E2E.

## Poziomy testów

### 1) Unit tests (preferowane)

- Serwisy (`app/services/*`)
- Funkcje pomocnicze
- Walidacje

### 2) API integration tests

- TestClient FastAPI
- Auth flow
- CRUD książek/notatek

### 3) SSR integration tests

- SSR routes renderują poprawny HTML
- Redirecty i ochrona stron

### 4) E2E (później) czyli werja v.2.0

- Playwright / Cypress / Selenium
- Uruchomienie aplikacji + klikanie

## Zasady

- Każdy bugfix powinien mieć test regresyjny (minimum 1).
- Testy nie mogą wymagać realnego OpenRouter.
  - AI należy mockować.

## CI

- `pytest -q` ma przechodzić bez dodatkowych usług (na ten etap).
