# Timeline — co i w jakiej kolejności dodaliśmy

Poniżej chronologia „najważniejszych cegiełek” projektu (MVP) w kolejności logicznej.

## 1) Szkielet aplikacji

- `app/main.py`
  - tworzy `FastAPI(title="BookCards")`
  - rejestruje routery (API + web)
  - serwuje pliki statyczne: `app.mount("/static", StaticFiles(directory="static"), name="static")`

## 2) Baza danych — fundamenty (bez modeli domenowych)

- `app/db/base.py`
  - `DeclarativeBase` (SQLAlchemy 2.0)

- `app/db/session.py`
  - konfiguracja engine i `sessionmaker`

- `app/api/deps.py`
  - dependency do wstrzykiwania sesji DB do endpointów

## 3) Routery API (placeholdery)

- `app/api/router.py`
  - agreguje routery modułów: `auth`, `books`, `notes`

- `app/api/auth.py`, `app/api/books.py`, `app/api/notes.py`
  - pliki „szkieletowe” z TODO

## 4) SSR UI (Jinja2)

- `app/web/router.py`
  - agreguje router SSR

- `app/web/books.py`
  - SSR endpoints:
    - `GET /books` (lista + pusta prawa kolumna)
    - `GET /books/{book_id}` (szczegóły książki + notatki)
    - `POST /books` (dodanie książki — placeholder: walidacja + redirect)
    - `POST /books/{book_id}/notes` (dodanie notatki — placeholder)
    - `POST /notes/{note_id}` (edycja notatki — placeholder)

- `templates/`
  - `base.html` — layout 2-kolumnowy
  - `books/index.html`, `books/detail.html`
  - `partials/_book_list.html` (lista książek + formularz dodania)
  - `partials/_note_card.html` (karta notatki + inline edit)

- `static/styles.css`
  - minimalistyczny CSS

## 5) OpenRouter service (AI) + testy

- `.windsurf/rules/openrouter-service-implementation-plan.md`
  - plan implementacji serwisu

- `app/services/openrouter_service.py`
  - async klient OpenRouter (`httpx`)
  - `chat_completion(...)`
  - `structured_output(...)`

- `tests/test_openrouter_service.py`
  - testy `unittest` z mockiem `httpx.AsyncClient`

## 6) Konfiguracja bezpieczeństwa (.env)

- `.gitignore`
  - ignoruje `.env*`
  - wyjątek: `!.env.example`

- `.env.example`
  - szablon env (bez sekretów)

- `app/core/settings.py`
  - centralny obiekt `settings` (env → atrybuty)
  - zawiera zarówno DB jak i OpenRouter
