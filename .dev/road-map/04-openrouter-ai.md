# AI / OpenRouter — stan i plan integracji

## Co jest gotowe

- `app/services/openrouter_service.py`
  - `chat_completion(...)` — podstawowe call do OpenRouter
  - `structured_output(...)` — structured outputs przez `response_format: json_schema`
  - mapowanie błędów: auth, rate limit, timeout, upstream, invalid response

- Test manualny (wykonany lokalnie)
  - prompt `ping` zwrócił `Pong! ...`

## Co NIE jest jeszcze wpięte

- brak `ai_service` (logika biznesowa: agregacja notatek, prompt, zapis wyników)
- brak `BackgroundTasks` uruchamianych przy dodaniu notatek
- brak DB persystencji wyników AI

## Zasady (twarde)

- AI nie może działać w request lifecycle.
- AI ma działać w tle (FastAPI `BackgroundTasks`).
- Logika AI ma być w `app/services`, nie w endpointach.

## Docelowy przepływ (MVP)

1. Endpoint tworzenia notatki zapisuje notatkę do DB.
2. Jeśli książka ma >= 3 notatki:
   - odpala `BackgroundTasks.add_task(ai_service.analyze_book, book_id)`
3. `ai_service.analyze_book(...)`:
   - pobiera notatki książki
   - buduje prompt
   - wywołuje `openrouter_service.structured_output(...)`
   - zapisuje wyniki do DB
   - aktualizuje status `processing/ready/failed`

## Konfiguracja

- `OPENROUTER_API_KEY` — wymagane
- `OPENROUTER_MODEL` — domyślnie `openai/gpt-4o-mini`
- `OPENROUTER_BASE_URL` — domyślnie `https://openrouter.ai/api/v1`
- `OPENROUTER_TIMEOUT_SECONDS` — domyślnie `30`

## Bezpieczeństwo

- nigdy nie commitujemy sekretów
- najlepiej ustawić limity kredytowe po stronie OpenRouter
