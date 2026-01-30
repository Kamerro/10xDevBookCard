# Stan projektu (na dziś) + co dalej

## Na czym stoi projekt

- Aplikacja FastAPI działa i ma SSR UI (Jinja2) dla widoku książek/notatek.
- SSR UI jest podpięte do DB (books + notes są pobierane i zapisywane).
- Serwis OpenRouter działa i ma testy jednostkowe.
- JSON API jest dostępne pod prefixem `/api`.

## Co jest MVP-done

- bootstrapped struktura projektu
- routing (API + web)
- SSR UI layout + formularze + CSS
- konfiguracja `.env` + bezpieczeństwo `.gitignore`
- OpenRouter service + testy
- CRUD dla książek i notatek
- Auth (rejestracja/logowanie) i ochrona endpointów

## Co jest jeszcze brakujące (kolejność sugerowana)

1. **AI pipeline (BackgroundTasks)**
   - `ai_service` + trigger po 3 notatkach
   - persystencja wyników AI + status badge

2. **Dokończenie UX + edge-case'y**
   - komunikaty 404/brak dostępu w SSR (obecnie proste redirecty)
   - dopięcie badge `processing` w SSR na liście książek (gdy będzie AI)
   - (opcjonalnie) doprecyzowanie rozdziału odpowiedzialności: SSR (cookie) vs API (Bearer)

## Otwarte uwagi

- Python REPL warning o `.python_history` to sprawa systemowa, nie projektowa.
