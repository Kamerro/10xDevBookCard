# After Each Change — CI Green Checklist

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](./governance.md)
> - [PRD](../01-product/prd.md)

Ten dokument to **checklista**, którą masz wykonać po każdej zmianie (fix/update/feature), żeby pipeline CI/CD przeszedł.

## 0) Zasada nadrzędna

- Jeśli zmieniasz kod, **musisz**:
  - utrzymać `ruff` green
  - utrzymać `pytest` green
  - utrzymać dependencies w spójnym stanie

## 1) Formatowanie i lint (obowiązkowe)

Uruchom lokalnie:

- `python -m ruff check .`
- `python -m ruff format --check .`

Jeśli format check failuje:

- `python -m ruff format .`
- potem ponownie:
  - `python -m ruff check .`
  - `python -m ruff format --check .`

## 2) Testy (obowiązkowe)

Uruchom lokalnie:

- `python -m pytest -q`

Jeśli zmiana dotyczy SSR/API:

- dopisz lub zaktualizuj test(y) w `tests/`

## 3) Zależności / requirements

Zasady:

- Każdy nowy import z zewnętrznej paczki => dopisz do `requirements.txt` (runtime) lub `requirements-dev.txt` (dev-only).
- Jeśli testy w CI padają na brak paczki, to znaczy, że dependency jest brakujące w `requirements*.txt`.

Po zmianach zależności:

- `python -m pip install -r requirements.txt`
- (opcjonalnie dev) `python -m pip install -r requirements-dev.txt`
- `python -m pytest -q`

## 4) Migracje DB (jeśli dotyczy)

Jeśli zmieniasz modele SQLAlchemy:

- musisz dodać migrację Alembic w `alembic/versions/`
- uruchom lokalnie migracje i testy

## 5) Sekrety i konfiguracja (security)

- Nigdy nie commituj sekretów.
- W `.env.example` tylko placeholdery.
- Nie loguj tokenów/JWT/kluczy.

## 6) Dokumenty `.ai` (governance)

Jeśli zmiana wpływa na architekturę, flow auth, AI pipeline, CI/CD albo inwarianty UX:

- zaktualizuj `.ai/GOVERNANCE.md`
- dopisz wpis w `Changelog`

## 7) CI sanity (co CI odpala)

W CI (GitHub Actions) odpala się m.in.:

- `Governance Check` (wymaga `.ai/GOVERNANCE.md` i `**Governance Version:**`)
- `ruff check .`
- `ruff format --check .`
- `pytest -q`
- `pip-audit -r requirements.txt`

Jeśli CI pada:

- najpierw odtwórz lokalnie dokładnie to samo polecenie
- dopiero potem zmieniaj config
