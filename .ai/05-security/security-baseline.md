# Security Baseline — BookCards

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](./GOVERNANCE.md)
> - [PRD](./prd.md)

## Cel

Minimalny, produkcyjny baseline bezpieczeństwa dla v1.0.

## Sekrety

- Zakaz commitowania sekretów.
- Włączone/wymagane na GitHub:
  - Secret scanning
  - Push protection

## Dependency Security

- `pip-audit -r requirements.txt` w CI.
- Dependabot weekly.

## SAST

- CodeQL włączony dla repo.

## Auth

- Hasła: `bcrypt`
- Tokeny: JWT
- SSR: cookie HttpOnly
- API: bearer

## Logging

- Nie logować:
  - tokenów
  - kluczy API
  - haseł
  - pełnych payloadów z danymi wrażliwymi

## AI / OpenRouter

- Klucz w env var.
- Brak sekretów w promptach/logach.
- Obsługa błędów upstream/rate limit.

## Minimalne wymagania przed release

- green: ruff, pytest, pip-audit
- brak sekretów w repo i historii (jeśli wyciekł secret => rotacja + purge)
