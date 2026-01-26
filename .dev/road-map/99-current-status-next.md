# Stan projektu (na dziś) + co dalej

## Na czym stoi projekt

- Aplikacja FastAPI działa i ma SSR UI (Jinja2) dla widoku książek/notatek.
- UI jest na placeholderach (brak realnych danych z DB w SSR).
- Serwis OpenRouter działa i ma testy jednostkowe.

## Co jest MVP-done

- bootstrapped struktura projektu
- routing (API + web)
- SSR UI layout + formularze + CSS
- konfiguracja `.env` + bezpieczeństwo `.gitignore`
- OpenRouter service + testy

## Co jest jeszcze brakujące (kolejność sugerowana)

1. **Modele SQLAlchemy + Alembic**
   - odwzorować `db-plan.md` w `app/models`
   - przygotować migracje

2. **CRUD w services + API**
   - books: create/list/get
   - notes: create/update

3. **Wpięcie SSR do DB**
   - `GET /books` i `GET /books/{id}` z realnymi danymi
   - `POST /books`, `POST /books/{id}/notes`, `POST /notes/{note_id}` zapisują do DB

4. **AI pipeline (BackgroundTasks)**
   - `ai_service` + trigger po 3 notatkach
   - persystencja wyników AI + status badge

5. **Auth**
   - rejestracja/logowanie
   - ochrona endpointów

## Otwarte uwagi

- Python REPL warning o `.python_history` to sprawa systemowa, nie projektowa.
