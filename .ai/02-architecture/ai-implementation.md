# AI Implementation (OpenRouter) — spec techniczna
 
 > **Najważniejsze dokumenty (source of truth)**
 > - [GOVERNANCE](../03-governance/governance.md)
 > - [PRD](../01-product/prd.md)
 
## Gdzie już jest opisane (źródła)

- `.ai/.windsurf/rules/openrouter-service-implementation-plan.md`
  - kontrakt API OpenRouter (`/chat/completions`), `response_format: json_schema`, mapa błędów, zasady bezpieczeństwa
  - docelowy flow: uruchamianie AI tylko w `BackgroundTasks`, po dodaniu >= 3 notatek
- `.ai/.dev/road-map/04-openrouter-ai.md`
  - stan wdrożenia (co jest gotowe / czego brakuje) + docelowy przepływ MVP
- `.ai/.dev/road-map/02-runtime-config.md`
  - wymagane/opsjonalne zmienne środowiskowe dla OpenRouter i uwagi dot. `.env`
- `.ai/tech-stack.md`
  - ogólny zakres AI (streszczenie, duplikaty, ranking ważności) + asynchroniczność

## Stan w kodzie (na dziś)

- `app/services/openrouter_service.py` jest już zaimplementowany i jest zgodny z powyższymi dokumentami:
  - `chat_completion(...)` — POST do OpenRouter
  - `structured_output(...)` — wymuszenie JSON schema (strict) + parsowanie JSON
  - wyjątki domenowe: auth / rate limit / timeout / upstream / invalid response

To jest **jedyny** element integracji AI, który jest już „produkcyjnie gotowy” na poziomie komunikacji z OpenRouter.

## Cel MVP (co ma robić AI)

AI przetwarza notatki książki i produkuje wynik zapisany w DB:

- **`summary`**: krótkie streszczenie książki na podstawie notatek
- **`duplicates`**: lista powtórzeń/duplikatów (np. grupy notatek o tym samym znaczeniu)
- **`importance_ranking`**: ranking ważności notatek

Wyniki są persystowane w tabeli `book_ai_analyses` (`BookAIAnalysis`).

## Twarde zasady (inwarianty)

- AI **nie może działać** w request lifecycle (endpoint nie może czekać na LLM).
- AI jest uruchamiane **wyłącznie** w tle przez FastAPI `BackgroundTasks`.
- Logika AI jest w `app/services`, nie w endpointach.
- Sekrety (klucze) nie trafiają do repo ani do logów.

## Konfiguracja (env)

- Wymagane:
  - `OPENROUTER_API_KEY`
- Opcjonalne:
  - `OPENROUTER_MODEL` (domyślnie `openai/gpt-4o-mini`)
  - `OPENROUTER_BASE_URL` (domyślnie `https://openrouter.ai/api/v1`)
  - `OPENROUTER_TIMEOUT_SECONDS` (domyślnie `30`)

Uwaga: samo posiadanie pliku `.env` nie oznacza, że Python automatycznie go wczyta.

## Kontrakt OpenRouter używany w projekcie

### Endpoint

- `POST {OPENROUTER_BASE_URL}/chat/completions`

### Headers

- `Authorization: Bearer <OPENROUTER_API_KEY>`
- `Content-Type: application/json`

### Body (minimal)

- `model: str`
- `messages: list[{role, content}]`

### Structured output (JSON schema)

Wymuszamy format:

- `response_format: { type: 'json_schema', json_schema: { name, strict: true, schema } }`

W kodzie to dokładnie robi `openrouter_service.structured_output(...)`.

## Obsługa błędów (mapowanie)

Mapowanie status code / błędów transportowych (zgodnie z `openrouter_service.py`):

- `401/403` => `OpenRouterAuthError`
- `429` => `OpenRouterRateLimitError`
- `>=500` => `OpenRouterUpstreamError`
- inne `4xx` => `OpenRouterUpstreamError` (request rejected)
- timeout => `OpenRouterTimeoutError`
- odpowiedź bez poprawnego JSON / bez `choices[0].message.content` => `OpenRouterInvalidResponseError`

## Docelowy przepływ funkcjonalny (MVP)

### Trigger

1. Użytkownik dodaje notatkę do książki.
2. System zapisuje notatkę w DB.
3. Jeśli książka ma **>= 3 notatki**, to uruchamia analizę AI w tle.

Dodatkowo:

4. Użytkownik edytuje notatkę.
5. System zapisuje zmiany notatki w DB.
6. Jeśli książka ma **>= 3 notatki**, to uruchamia analizę AI w tle.

### Gdzie to podpiąć

- Tylko API:
  - `POST /api/books/{book_id}/notes` (create note)
  - `PUT /api/notes/{note_id}` (update note)

Po udanym zapisie notatki endpoint powinien:

- policzyć liczbę notatek książki
- jeśli >= 3, dodać task: `BackgroundTasks.add_task(ai_service.analyze_book, book_id=..., user_id=...)`

Uwaga: obecnie w repo jest helper `count_notes_for_book(...)` w `app/services/note_service.py`, który można wykorzystać.

## `ai_service` — odpowiedzialności (do zaimplementowania)

Plik: `app/services/ai_service.py` (docelowo)

### `analyze_book(book_id, user_id)`

- **Wejście**:
  - `book_id` (UUID)
  - `user_id` (UUID) — żeby wymusić autoryzację na warstwie services (nie analizujemy cudzej książki)
- **Kroki**:
  - pobierz książkę + notatki z DB
  - waliduj warunek: jeśli notatek < 3 => zakończ (no-op)
  - ustaw / utwórz rekord `BookAIAnalysis`:
    - `analysis_status='processing'`
    - wyczyść `analysis_error`
  - zbuduj `messages` (system + user) oraz JSON schema dla odpowiedzi
  - wywołaj `openrouter_service.structured_output(...)`
  - zapisz wynik do DB:
    - `analysis_status='ready'`
    - `summary`, `duplicates`, `importance_ranking`
    - `analyzed_at=now()`
  - w razie błędu:
    - `analysis_status='failed'`
    - `analysis_error=str(e)` (bez sekretów)

## Szybkie edycje notatek (debounce, współbieżność, koalescencja)

Jeśli użytkownik szybko edytuje notatki, endpoint będzie potencjalnie dodawał wiele tasków do `BackgroundTasks`. Żeby nie generować niepotrzebnych calli do OpenRouter i nie zapisywać „starych” wyników, wdrożenie musi mieć mechanizm koalescencji.

### Wymaganie

- Dla danej książki w danym momencie może być wykonywana **co najwyżej jedna** analiza AI.
- Jeśli w trakcie analizy notatki się zmieniły, wynik aktualnej analizy **nie może nadpisać** nowszych danych (albo musi być uznany za nieaktualny i pominięty).

### Rekomendowany mechanizm (DB-based, implementowalny na wielu workerach)

1) Dodaj do `BookAIAnalysis` dwa pola (wymaga migracji):

- `analysis_version: int` (domyślnie `0`)
- `requested_version: int` (domyślnie `0`)

### Migracja DB (wymagana)

#### Zmiany w modelu

W `app/models/book_ai_analysis.py` dodaj pola:

- `analysis_version`: integer, `nullable=False`, default `0`
- `requested_version`: integer, `nullable=False`, default `0`

Docelowo (dokładna intencja):

- `analysis_version` oznacza wersję notatek, dla której zapisany wynik jest aktualny.
- `requested_version` oznacza najnowszą wersję notatek, która powinna być przeanalizowana.

#### Alembic

Utwórz nową migrację (preferowane):

- `alembic revision -m "add ai versions"`

W `upgrade()` dodaj:

- `op.add_column('book_ai_analyses', sa.Column('analysis_version', sa.Integer(), nullable=False, server_default='0'))`
- `op.add_column('book_ai_analyses', sa.Column('requested_version', sa.Integer(), nullable=False, server_default='0'))`

Po migracji (opcjonalnie, porządki):

- usuń `server_default` jeśli nie chcesz go utrzymywać po stronie DB i polegasz na defaultach aplikacji

W `downgrade()` usuń kolumny:

- `op.drop_column('book_ai_analyses', 'requested_version')`
- `op.drop_column('book_ai_analyses', 'analysis_version')`

Uwaga: ponieważ `BookAIAnalysis` ma relację 1:1 do książki (`book_id` unique), te pola działają jako naturalny „scheduler” per book.

2) Logika w endpointach (create/update note):

- Po zapisie notatki, jeśli `count_notes_for_book >= 3`:
  - `ai.requested_version += 1` (lub ustaw na `analysis_version + 1`)
  - jeśli `analysis_status != 'processing'`: ustaw `analysis_status='processing'` i dodaj task
  - jeśli `analysis_status == 'processing'`: **nie dodawaj** kolejnego taska (tylko podbij `requested_version`)

3) Logika w `ai_service.analyze_book(...)`:

- Na starcie odczytaj `requested_version` i zapamiętaj w lokalnej zmiennej `target_version`.
- Po wyliczeniu wyniku, przed zapisem:
  - odczytaj ponownie rekord `BookAIAnalysis`
  - jeśli `requested_version != target_version`: oznacza to, że przyszła nowsza edycja → **nie zapisuj** wyniku, tylko uruchom kolejną analizę (re-run) albo zakończ i pozwól, by kolejny task to obsłużył.
  - jeśli `requested_version == target_version`: zapisz wynik i ustaw `analysis_version = target_version`, `analysis_status='ready'`.

Ten schemat zapewnia:

- debounce (wiele edycji „skleja się” do jednego uruchomienia)
- odporność na race conditions
- poprawne działanie przy wielu instancjach aplikacji

### Minimalny fallback (tylko single-process dev)

Jeśli nie chcesz robić migracji w MVP-dev, możesz zastosować in-memory lock per `book_id`, ale to jest poprawne tylko dla pojedynczego procesu i nie powinno iść na produkcję.

### Statusy

Utrzymujemy spójne statusy w `BookAIAnalysis.analysis_status`:

- `pending` — brak rekordu lub jeszcze nie wyliczone
- `processing` — analiza w toku
- `ready` — wynik zapisany
- `failed` — błąd + `analysis_error`

## Format wyników (JSON schema)

Minimalny kontrakt (gotowy do wdrożenia) — obiekt JSON:

- `summary`: string
- `duplicates`: array[DuplicateGroup]
- `importance_ranking`: array[ImportanceItem]

### DuplicateGroup

- `note_numbers`: array[int] (min 2)
- `reason`: string

### ImportanceItem

- `note_number`: int
- `score`: int (1-10)
- `reason`: string

### JSON schema (do użycia w `structured_output`)

`schema_name`: `book_ai_analysis_v1`

`json_schema`:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["summary", "duplicates", "importance_ranking"],
  "properties": {
    "summary": {"type": "string", "minLength": 1},
    "duplicates": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["note_numbers", "reason"],
        "properties": {
          "note_numbers": {
            "type": "array",
            "minItems": 2,
            "items": {"type": "integer", "minimum": 1}
          },
          "reason": {"type": "string", "minLength": 1}
        }
      }
    },
    "importance_ranking": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["note_number", "score", "reason"],
        "properties": {
          "note_number": {"type": "integer", "minimum": 1},
          "score": {"type": "integer", "minimum": 1, "maximum": 10},
          "reason": {"type": "string", "minLength": 1}
        }
      }
    }
  }
}
```

Wyniki zapisujemy 1:1 do `BookAIAnalysis.summary`, `BookAIAnalysis.duplicates`, `BookAIAnalysis.importance_ranking`.

Uwaga: implementacja musi upewnić się, że `note_number` i `note_numbers` odnoszą się do numeracji `Note.number` (unikalnej per książka), nie do UUID notatki.

## Prompty (gotowe do wdrożenia)

### `messages[0]` — system

`role`: `system`

`content`:

"Jesteś asystentem, który analizuje notatki do książki. Zwracasz WYŁĄCZNIE JSON zgodny ze schematem. Nie dodawaj żadnego tekstu poza JSON. Jeśli informacji jest za mało, nadal zwróć poprawny JSON i zrób rozsądne, ostrożne wnioski." 

### `messages[1]` — user

`role`: `user`

`content` powinien zawierać:

- tytuł i autora książki
- listę notatek w kolejności rosnącej po `Note.number`

Format (dokładny):

"Tytuł: {title}\nAutor: {author}\n\nNotatki (number: content):\n{n1}\n{n2}\n...\n\nZadanie:\n1) Napisz summary.\n2) Wykryj duplikaty znaczeniowe i podaj grupy note_numbers.\n3) Oceń ważność każdej notatki (1-10) i podaj importance_ranking." 

## Logging

- Logujemy:
  - status code / typ błędu / czas trwania / model
- Nie logujemy:
  - API key
  - pełnych promptów (ew. tylko lokalnie w debug)

## Testowanie

- Unit testy dla `ai_service`:
  - mock `openrouter_service.structured_output`
  - przypadki: <3 notatki => no-op, happy path => zapis wyników, error path => `failed`
- Testy integracyjne (opcjonalnie):
  - tylko lokalnie, bez commitowania klucza

## Out of scope (na teraz)

- Konfigurowalne prompty w UI
- Streamowanie odpowiedzi
- Kolejki (Celery/RQ) — na MVP wystarczą `BackgroundTasks`
- Re-analiza przy każdej zmianie notatki (można doprecyzować później)
