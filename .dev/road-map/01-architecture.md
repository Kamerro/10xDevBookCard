# Architektura — komponenty i połączenia

To jest „mapa połączeń” w projekcie. Bez ozdobników.

## Warstwy (zgodnie z rules)

- **API layer (`app/api`)**
  - odpowiedzialność: HTTP, walidacja, autoryzacja, DI
  - brak logiki biznesowej

- **Web/SSR layer (`app/web`, `templates`)**
  - odpowiedzialność: renderowanie HTML (Jinja2), obsługa formularzy
  - SSR korzysta bezpośrednio z `app/services` i zapisuje/odczytuje dane z DB

- **Services (`app/services`)**
  - odpowiedzialność: logika biznesowa
  - AI integracja tu (nie w endpointach)

- **DB (`app/db`)**
  - odpowiedzialność: konfiguracja SQLAlchemy

- **Models (`app/models`)**
  - docelowo: mapowania SQLAlchemy (na razie praktycznie pusto)

## Przepływ requestów (dziś)

### SSR: `/books` i `/books/{id}`

1. `FastAPI` w `app/main.py`
2. `app/web/router.py` → `app/web/books.py`
3. endpoint składa `context` z danych z DB (przez `app/services/*_service.py`)
4. `Jinja2Templates` renderuje `templates/books/*.html`
5. `base.html` includuje `partials/_book_list.html`
6. CSS ładuje się z `/static/styles.css`

### SSR POST (formularze)

- `POST /books` → `create_book()`
  - walidacja: `title` i `author` niepuste
  - przy błędzie: renderuje `books/index.html` z `error_add_book`
  - sukces: redirect `303` do `/books`

- `POST /books/{book_id}/notes` → `create_note()`
  - walidacja: `content` niepusty

- `POST /notes/{note_id}` → `update_note()`
  - walidacja: `content` niepusty

Uwaga: te POSTy zapisują do DB przez serwisy.

## Routing: rozdzielenie SSR vs JSON API

- SSR działa na ścieżkach typu `/books`, `/login`.
- JSON API jest mountowane pod prefixem **`/api`** (np. `/api/books`).

## Auth: SSR vs JSON API

- SSR:
  - po loginie/rejestracji ustawia cookie `access_token`
  - widoki SSR dekodują JWT z cookie i pobierają usera z DB
- JSON API:
  - oczekuje `Authorization: Bearer <access_token>`
  - dependency `get_current_user` w `app/api/deps.py`

## Przepływ AI (dziś)

- `app/services/openrouter_service.py`
  - jest gotowy do użycia w services
- Docelowo:
  - endpoint tworzący notatkę (API/SSR) zapisze notatkę do DB
  - jeśli liczba notatek >= 3:
    - uruchomi `BackgroundTasks` → `ai_service.analyze_book(...)`
    - `ai_service` wywoła `openrouter_service.structured_output(...)`
    - wyniki zostaną zapisane w DB

## Miejsca „source of truth”

- `.ai/prd.md` — wymagania produktu
- `.ai/tech-stack.md` — technologie
- `.windsurf/rules/*.mdc` — zasady architektury i stylu
- `.windsurf/rules/*-implementation-plan.md` — plany wdrożeniowe
