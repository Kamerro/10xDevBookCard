# BookCards (MVP)

BookCards to prosta aplikacja webowa do budowania prywatnej biblioteki książek oraz dodawania notatek w trakcie czytania. Po dodaniu odpowiedniej liczby notatek AI będzie analizować notatki per książka (asynchronicznie), zapisując wyniki w bazie danych.

Ten commit/repo jest na etapie **bootstrapa**: struktura projektu + minimalna konfiguracja. Bez implementacji logiki biznesowej i bez gotowych endpointów.

## Tech stack (MVP)

- Python 3.13.4
- FastAPI (REST + OpenAPI)
- PostgreSQL
- SQLAlchemy 2.0 (planowane migracje: Alembic)
- Pydantic v2
- SSR: Jinja2 (poza zakresem bootstrapa, przygotowanie później)
- BackgroundTasks dla zadań AI (poza zakresem bootstrapa)

## Struktura projektu

```text
app/
  main.py              # Inicjalizacja FastAPI
  core/settings.py      # Minimalne ustawienia (env)
  api/                  # Warstwa HTTP (bez logiki biznesowej)
    router.py           # Agregacja routerów
    deps.py             # Zależności (np. DB session)
    auth.py             # Moduł auth (placeholder)
    books.py            # Moduł books (placeholder)
    notes.py            # Moduł notes (placeholder)
  db/
    base.py             # SQLAlchemy Declarative Base
    session.py          # Engine + SessionLocal
  models/               # Modele SQLAlchemy (na razie tylko Base re-export)
  services/             # Serwisy (logika biznesowa/AI) – na razie puste
```

## Konfiguracja

Aplikacja używa zmiennej środowiskowej `DATABASE_URL`.

Domyślna wartość (dev):

```text
postgresql+psycopg://postgres:postgres@localhost:5432/bookcards
```

## Uruchomienie lokalne (dev)

1. Ustaw Python 3.13.4.
2. Uruchom PostgreSQL i utwórz bazę `bookcards`.
3. Ustaw `DATABASE_URL` (jeśli inne niż domyślne).
4. Zainstaluj zależności (plik zależności nie został jeszcze dodany w repo; dodamy go jako osobny krok).
5. Start serwera:

```bash
python -m uvicorn app.main:app --reload
```

Po starcie dokumentacja OpenAPI będzie dostępna pod:

- `http://127.0.0.1:8000/docs`

## Co jest gotowe

- FastAPI app initialization (`app/main.py`)
- Wspólny router API (`app/api/router.py`)
- Zależność DI dla sesji DB (`app/api/deps.py`)
- SQLAlchemy 2.0 base + session (`app/db/base.py`, `app/db/session.py`)
- Puste moduły API: `auth`, `books`, `notes` (z `TODO`)

## Co NIE jest zaimplementowane (celowo)

- Auth (rejestracja / logowanie / reset hasła)
- Endpointy dla książek i notatek
- Modele SQLAlchemy dla `User`, `Book`, `Note`
- Migracje Alembic
- AI / OpenRouter integracja
- SSR widoki (Jinja2)

## Zasady (MVP)

- API (`app/api`) zawiera tylko HTTP + walidację + zależności (bez logiki)
- Logika biznesowa i AI trafi do `app/services`
- Modele w `app/models` nie zawierają logiki
- AI będzie uruchamiane wyłącznie w `BackgroundTasks` (bez blokowania requestów)
