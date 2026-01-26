# Testy

## Co mamy

- `tests/test_openrouter_service.py`
  - testy `unittest` (offline)
  - mock `httpx.AsyncClient`
  - testy:
    - success
    - auth error (401)
    - rate limit (429)
    - timeout
    - invalid json
    - invalid shape
    - structured_output parsing

## Jak uruchomić

Z katalogu repo:

```powershell
python -m unittest
```

Tylko serwis OpenRouter:

```powershell
python -m unittest tests.test_openrouter_service
```

## Wymagania

- `httpx` musi być zainstalowany, bo jest importowany w serwisie.

Testy nie wykonują połączeń sieciowych.
