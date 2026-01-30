# Tech Stack – BookCards (MVP)

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](./GOVERNANCE.md)
> - [PRD](./prd.md)

## 1. Język i runtime
- Language: Python 3.13.4
- Typowanie: standard typing + Pydantic
- Styl: prosty, czytelny, bez nadmiarowych abstrakcji

---

## 2. Backend
- Framework: FastAPI
- Architektura: modularna (api / services / models)
- Komunikacja: REST (JSON)
- Walidacja danych: Pydantic
- Dokumentacja API: OpenAPI (wbudowana w FastAPI)

---

## 3. Autoryzacja i bezpieczeństwo
- Auth: email + hasło
- Hashowanie haseł: bcrypt
- Autoryzacja: JWT (access token)
- Reset hasła: token wysyłany emailowo
- Ochrona endpointów: zależności FastAPI
- Brak OAuth / SSO (poza zakresem MVP)

---

## 4. Baza danych
- Silnik: PostgreSQL
- ORM: SQLAlchemy 2.0
- Migracje: Alembic
- Relacje:
  - User → Books (1:N)
  - Book → Notes (1:N)
- Przechowywanie wyników AI w bazie danych

---

## 5. AI / LLM
- Dostęp do modeli: OpenRouter API
- Integracja: bezpośrednie wywołania HTTP
- Zakres:
  - streszczanie notatek
  - wykrywanie powtórzeń
  - ocena ważności notatek
- AI działa asynchronicznie
- Brak konfigurowalnych promptów w UI

---

## 6. Przetwarzanie asynchroniczne
- Mechanizm: FastAPI BackgroundTasks (MVP)
- AI uruchamiane po dodaniu ≥3 notatek do książki
- Brak blokowania requestów użytkownika
- Możliwość rozbudowy o kolejkę (Celery / RQ) poza MVP

---

## 7. Frontend
- Rendering: server-side (Jinja2)
- Stylowanie: minimalistyczne CSS
- UX:
  - ultra prosty layout
  - wyraźny widok „Dodaj książkę”
  - estetyczna forma notatek (fiszki)
- Brak SPA / frameworków JS (MVP)

---

## 8. Testy
- Framework: pytest
- Zakres:
  - test logiki AI (mock LLM)
  - test kluczowych endpointów API
- Co najmniej jeden sensowny test wymagany do zaliczenia

---

## 9. CI / CD
- Platforma: GitHub Actions
- Kroki:
  - instalacja zależności
  - uruchomienie testów pytest
- Brak automatycznego deployu (opcjonalnie)

---

## 10. Hosting i deployment
- Platforma: Fly.io
- Forma: Docker container
- Konfiguracja:
  - zmienne środowiskowe (.env)
  - osobne ustawienia dla dev / prod
- Brak AWS / Azure

---

## 11. Świadomie wykluczone
- Microservices
- Event-driven architecture
- GraphQL
- Kubernetes
- Frontend SPA
- Multi-tenancy
- High availability

---

## 12. Status dokumentu
- Wersja: 1.0
- Zakres: MVP
- Dokument stanowi techniczny kontekst referencyjny dla AI
