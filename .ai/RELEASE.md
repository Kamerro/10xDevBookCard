# Release — BookCards (v1.0)

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](./GOVERNANCE.md)
> - [PRD](./prd.md)

## Cel

Ten dokument opisuje **procedurę wydania** (release) i hotfixów dla BookCards.

## Zakres

- Release 1.0 (MVP)
- Hotfix releases (1.0.x)

## Pre-release checklist (lokalnie)

- `python -m ruff check .`
- `python -m ruff format --check .`
- `python -m pytest -q`
- (opcjonalnie) `pip-audit -r requirements.txt`

## Migracje DB

Jeśli release zawiera zmianę modeli:

- upewnij się, że istnieje migracja w `alembic/versions/`
- zweryfikuj upgrade/downgrade na lokalnym środowisku
- w release notes dopisz "DB migration required"

## Zasady wersjonowania

- SemVer:
  - `MAJOR` – breaking change (docelowo rzadko)
  - `MINOR` – nowe funkcje kompatybilne
  - `PATCH` – hotfix

## Proces wydania (propozycja)

1) Zaktualizuj `.ai/GOVERNANCE.md` jeśli release zmienia zasady/flow/architekturę.
2) Uruchom checklistę pre-release.
3) Wypchnij zmiany na `main` (po przejściu CI).
4) Utwórz tag: `vX.Y.Z`.
5) Utwórz Release w GitHub (release notes).

## Hotfix

- twórz minimalne PR-y
- wymagaj testu pokrywającego regresję
- bump tylko `PATCH`
