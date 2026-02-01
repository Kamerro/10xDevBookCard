# Deploy Commands for Fly.io

## 1. Zaloguj się do Fly.io
```bash
fly auth login
```

## 2. Ustaw zmienne środowiskowe (jeśli jeszcze nie ustawione)
```bash
fly secrets set SECRET_KEY="twoj-super-tajny-klucz-min-32-znakow"
fly secrets set OPENROUTER_API_KEY="twoj-klucz-openrouter"
fly secrets set OPENROUTER_MODEL="openai/gpt-4o-mini"
```

## 3. Deploy aplikacji z naprawionymi plikami statycznymi
```bash
fly deploy
```

## 4. Sprawdź status aplikacji
```bash
fly status
```

## 5. Otwórz aplikację w przeglądarce
```bash
fly open
```

## 6. Sprawdź logi w razie problemów
```bash
fly logs
```

## Rozwiązywanie problemów:

### Jeśli CSS nadal nie działa:
```bash
# Sprawdź czy pliki statyczne są w kontenerze
fly ssh console
ls -la /app/static/
```

### Jeśli aplikacja nie startuje:
```bash
# Sprawdź logi błędów
fly logs --recent
```

### Jeśli baza danych nie działa:
```bash
# Sprawdź status bazy danych
fly postgres list
```
