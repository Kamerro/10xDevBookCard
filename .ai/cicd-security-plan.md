# CI/CD + Security Plan (GitHub Actions)

## Cel

- Kod na GitHub ma być automatycznie sprawdzany pod kątem:
  - bezpieczeństwa (SAST, dependency vulnerabilities, secret scanning)
  - poprawności/quality (lint + format)
  - uruchamiania testów jednostkowych
- Checki mają blokować merge do `main` (branch protection).
- Ma być możliwość ręcznego uruchamiania testów z poziomu workflow (`workflow_dispatch`).
- Na ten etap: **bez odpalania bazy danych w CI** (brak service containers). E2E w kolejnym kroku.

## Założenia

- Python: **ta sama wersja, na której projekt aktualnie działa lokalnie** (jedna wersja w workflow, bez matrixa).
- Lint/format: **ruff** (bez black).

## Workflow: `.github/workflows/ci.yml`

### Triggery

- `pull_request` (na `main`)
- `push` (na `main`)
- `workflow_dispatch` (manual)

### Joby

1) `lint`

- `ruff check .`
- `ruff format --check .`

2) `tests`

- Instalacja zależności
- `pytest -q`
- Bez bazy w CI

3) `dep-audit`

- `pip-audit -r requirements.txt`

### Manual triggers (`workflow_dispatch`)

- Input: `test_path` (domyślnie `tests/`)
- Input: `pytest_args` (opcjonalnie)

### Performance

- Cache pip przez `actions/setup-python` (cache `pip`).

## Workflow: `.github/workflows/codeql.yml` (SAST)

### Triggery

- `pull_request`
- `push` (na `main`)
- `schedule` (np. 1x/tydzień)
- (opcjonalnie) `workflow_dispatch`

### Konfiguracja

- Language: `python`
- Standardowe queries GitHub

## Workflow: `.github/workflows/dependency-review.yml`

- Trigger: `pull_request`
- Action: `actions/dependency-review-action`
- Cel: blokować PR, jeśli zmiana dependencies wprowadza znane podatności.

## Dependabot

Plik: `.github/dependabot.yml`

- Ekosystem: `pip`
- Harmonogram: weekly
- Cel: regularne PR z aktualizacjami zależności + security updates.

## Konfiguracja repo (GitHub Settings)

### Code security and analysis

Włączyć:

- Code scanning: **CodeQL**
- **Secret scanning** + push protection
- **Dependabot alerts**
- **Dependabot security updates**

### Branch protection dla `main`

- Require status checks:
  - `ci / lint`
  - `ci / tests`
  - `ci / dep-audit`
  - `codeql`
  - `dependency-review`
- Block merge jeśli którykolwiek check jest red.

## Zmiany w repo (pliki konfiguracyjne)

- `pyproject.toml`:
  - konfiguracja `ruff`
- (preferowane) `requirements-dev.txt`:
  - `ruff`
  - `pip-audit`
  - (pytest jest już używany w projekcie)

## Kolejność wdrożenia

1) Dodać `pyproject.toml` i skonfigurować `ruff`.
2) Dodać `ci.yml` (lint + tests + dep-audit).
3) Dodać `codeql.yml`.
4) Dodać `dependabot.yml` i `dependency-review.yml`.
5) Włączyć security settings w GitHub + branch protection.

## Definition of Done

- PR bez green checks nie da się zmergować do `main`.
- `workflow_dispatch` pozwala odpalić testy ręcznie.
- CodeQL i dependency review działają na PR i w cyklicznych skanach.
- Secret scanning blokuje przypadkowe commity sekretów.
