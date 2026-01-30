# Plan implementacji — OpenRouter service (MVP)

## Cel

Zaimplementować minimalny, bezpieczny serwis do komunikacji z OpenRouter (chat completions), który będzie używany wyłącznie w logice biznesowej (`app/services`) oraz uruchamiany w tle (FastAPI `BackgroundTasks`) zgodnie z rules.

Zakres tej lekcji to dostarczenie fundamentu integracji z LLM:

- poprawne requesty do OpenRouter
- obsługa błędów i timeouts
- możliwość wymuszenia structured output (json_schema)
- łatwe mockowanie w testach

Bez:

- kluczy w repo
- wywołań AI w request lifecycle
- implementacji promptów per funkcja (to osobny krok)

---

## Source of truth

- Tech stack: `.ai/tech-stack.md`
- Rules:
  - `.windsurf/rules/ai.mdc` (AI tylko w BackgroundTasks)
  - `.windsurf/rules/backend.mdc` (logika w services)
  - `.windsurf/rules/shared.mdc`

---

## Konfiguracja

### Zmienne środowiskowe

- `OPENROUTER_API_KEY` (w `.env`, nie commitujemy)

Opcjonalne (MVP, ale wygodne):

- `OPENROUTER_MODEL` (np. `openai/gpt-4o-mini`)
- `OPENROUTER_BASE_URL` (domyślnie `https://openrouter.ai/api/v1`)
- `OPENROUTER_TIMEOUT_SECONDS` (np. `30`)

### Bezpieczeństwo

- Klucz nigdy nie trafia do logów.
- W README/konfiguracji przypominamy o limicie kredytowym po stronie OpenRouter.

---

## Biblioteki

Ponieważ to Python i FastAPI, proponowany klient HTTP:

- `httpx` (async)

Uwaga: nie blokujemy event loop.

---

## Kontrakt API OpenRouter (dla serwisu)

### Endpoint

- `POST https://openrouter.ai/api/v1/chat/completions`

### Headers

- `Authorization: Bearer <OPENROUTER_API_KEY>`
- `Content-Type: application/json`

### Body (minimal)

- `model: str`
- `messages: list[{role, content}]`

### Structured outputs

OpenRouter wspiera `response_format` w wariancie:

- `response_format: { type: 'json_schema', json_schema: { name: '<name>', strict: true, schema: <json_schema_obj> } }`

W Pythonie przechowujemy to jako normalny dict.

---

## Projekt: struktura plików

- `app/services/openrouter_service.py`
  - serwis OpenRouter
- `app/services/openrouter_types.py` (opcjonalnie)
  - Pydantic modele odpowiedzi, jeżeli chcemy typować odpowiedzi

Zasada MVP: nie przesadzamy z warstwami; jeśli modele Pydantic są krótkie, można je trzymać w `openrouter_service.py`.

---

## Interfejs serwisu (propozycja MVP)

### Funkcje

1) `async def chat_completion(*, model: str, messages: list[dict], response_format: dict | None = None) -> dict`

- Zwraca surową odpowiedź jako dict (MVP).
- Walidacja minimalna: sprawdzenie, że `choices[0].message.content` istnieje.

2) `async def structured_output(*, model: str, messages: list[dict], schema_name: str, json_schema: dict) -> dict`

- Buduje `response_format` (json_schema strict) i wywołuje `chat_completion`.
- Parsuje `content` jako JSON (z `json.loads`).
- Jeśli parsowanie się nie uda: rzuca wyjątek domenowy.

### Wyjątki (MVP)

- `OpenRouterAuthError`
- `OpenRouterRateLimitError`
- `OpenRouterUpstreamError` (5xx)
- `OpenRouterTimeoutError`
- `OpenRouterInvalidResponseError`

---

## Obsługa błędów

- Timeout: jawny timeout w `httpx.AsyncClient(timeout=...)`
- Status codes:
  - `401/403` → auth error
  - `429` → rate limit
  - `>=500` → upstream error
  - inne `4xx` → invalid request / upstream validation

Wszystkie błędy mapujemy na wyjątki serwisu.

---

## Logowanie (minimalne)

- Logujemy tylko:
  - status code
  - model
  - czas trwania
- Nie logujemy:
  - API key
  - pełnych promptów (opcjonalnie tylko w debug local)

---

## Testowalność

- Serwis powinien umożliwiać podmianę klienta HTTP (np. dependency injection parametrem lub funkcją fabrykującą klienta).
- Alternatywnie: mock `httpx.AsyncClient.post`.

---

## Integracja z BookCards (następny krok po serwisie)

- `app/services/ai_service.py`:
  - agreguje notatki dla książki
  - buduje prompt
  - wywołuje `openrouter_service.structured_output(...)`
  - zapisuje wyniki w DB (zgodnie z `db-plan.md`)

Uruchamianie:

- tylko z `BackgroundTasks` po dodaniu >= 3 notatek (zgodnie z rules).

---

## Workflow 3×3 (implementacja serwisu)

### Iteracja 1 (3 kroki)

1. Dodać zależność `httpx` (na razie manualnie w środowisku; plik zależności dodamy osobno).
2. Utworzyć `app/services/openrouter_service.py` z minimalnym `chat_completion`.
3. Dodać wyjątki domenowe + mapowanie status code.

### Iteracja 2 (3 kroki)

1. Dodać `structured_output` z `response_format` json_schema.
2. Dodać parsowanie JSON + błąd `OpenRouterInvalidResponseError`.
3. Dodać minimalne testy jednostkowe (mock httpx).

### Iteracja 3 (3 kroki)

1. Dodać integracyjny test manualny (z FREE modelem lub tanim modelem) — bez commitowania klucza.
2. Dodać opis konfiguracji `.env` (w README lub osobnym dokumencie).
3. Dodać minimalną funkcję pomocniczą w `ai_service.py` (bez podpinania do endpointów).
