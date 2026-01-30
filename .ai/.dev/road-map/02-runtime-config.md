# Runtime / konfiguracja / env

## Pliki

- `.env` — lokalnie, **nie commitujemy** (ignorowany)
- `.env.example` — szablon, commitujemy
- `.gitignore` — ignoruje `.env*`, ale trzyma `!.env.example`

## Settings

- `app/core/settings.py`
  - `settings.database_url`
  - `settings.openrouter_api_key`
  - `settings.openrouter_model`
  - `settings.openrouter_base_url`
  - `settings.openrouter_timeout_seconds`

## OpenRouter

Wymagane:

- `OPENROUTER_API_KEY`

Opcjonalne:

- `OPENROUTER_MODEL` (domyślnie `openai/gpt-4o-mini`)
- `OPENROUTER_BASE_URL` (domyślnie `https://openrouter.ai/api/v1`)
- `OPENROUTER_TIMEOUT_SECONDS` (domyślnie `30`)

## Jak ustawić zmienne na Windows (PowerShell)

Tymczasowo (tylko w bieżącej sesji terminala):

```powershell
$env:OPENROUTER_API_KEY="..."
```

Uwaga: samo istnienie pliku `.env` **nie** oznacza, że Python go automatycznie wczyta.
