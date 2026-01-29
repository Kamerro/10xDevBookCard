# Test Plan — BookCards (MVP)

## 1. Cel i zakres
Celem testów jest potwierdzenie, że MVP BookCards działa end-to-end w obszarach:

- **DB**: Postgres + migracje Alembic + healthcheck
- **Auth (API)**: rejestracja i logowanie
- **Auth (UI SSR)**: rejestracja, logowanie, logout, cookie JWT
- **Kontrola dostępu (UI SSR)**: `/books` i akcje powiązane wymagają cookie

Zakres jest dopasowany do aktualnego stanu codebase (MVP).

## 2. Elementy w zakresie / poza zakresem

### W zakresie
- DB
  - `python -m alembic upgrade head`
  - `GET /health/db`
- Auth API
  - `POST /auth/register`
  - `POST /auth/login`
- Auth UI
  - `GET /register` + `POST /register` (tworzy usera w DB, auto-login cookie)
  - `GET /login` + `POST /login` (cookie, redirect)
  - `POST /logout` (czyści cookie)
- Dostęp
  - `/books`, `/books/{id}`, `POST /books`, `POST /books/{id}/notes`, `POST /notes/{id}` wymagają cookie `access_token` (redirect do `/login` jeśli brak)

### Poza zakresem (na teraz)
- Reset hasła (email, token, formularz ustawienia nowego hasła)
- Rate limiting, CSRF, WAF itp. (opisane w ryzykach)
- CRUD books/notes w DB (obecnie widoki są placeholder; testujemy tylko dostęp/routing)
- Analiza AI

## 3. Założenia i ograniczenia (MVP)
- Środowisko: Windows + PowerShell.
- DB: Postgres w Docker Desktop (lokalnie).
- Auth: JWT w cookie `access_token` (HttpOnly, SameSite=Lax).
- Wymagania hasła (MVP):
  - długość **8–19**
  - min. **1 wielka litera**
  - min. **1 cyfra**
  - min. **1 znak specjalny**

## 4. Środowisko testowe

### Konfiguracja
- `DATABASE_URL=postgresql+psycopg://bookcards:bookcards@localhost:5432/bookcards`
- `SECRET_KEY=<ustawione>`

### Komendy
- Start DB (jeśli kontener istnieje): `docker start bookcards-postgres`
- Migracje: `python -m alembic upgrade head`
- Start app: `python -m uvicorn app.main:app --reload`

### Endpointy kontrolne
- Swagger: `http://127.0.0.1:8000/docs`
- DB health: `http://127.0.0.1:8000/health/db`

## 5. Dane testowe + strategia czyszczenia

### Użytkownicy
- `qa.user1@example.com` / `Password1!`
- `qa.user2@example.com` / `Password1!`

### Czyszczenie
Najprościej w dev:
- reset DB przez wyczyszczenie danych (psql) lub nowy kontener.

## 6. Typy testów
- **Smoke (P0)**: DB, migracje, register/login/logout, ochrona `/books`.
- **Negatywne (P1)**: walidacje haseł, duplikat email, błędne dane logowania.
- **Security sanity (P2)**: cookie flags, brak ujawniania szczegółów auth, ryzyka.

## 7. Kryteria wejścia/wyjścia

### Entry criteria
- Kontener Postgresa działa.
- `DATABASE_URL` i `SECRET_KEY` ustawione.
- Migracje wykonane (`upgrade head`).
- Aplikacja startuje bez exceptionów.

### Exit criteria
- Wszystkie testy P0 przechodzą.
- P1 przechodzą lub mają zarejestrowane defekty.
- Ryzyka MVP są opisane.

## 8. Ryzyka i mitigacje
- **Brak CSRF** przy cookie auth: ryzyko; mitigacja: CSRF token / double-submit w przyszłości.
- **Brak rate limiting** na login/register: ryzyko brute force; mitigacja: limit + captcha po X próbach.
- **Brak weryfikacji JWT przy /books** (obecnie sprawdzamy tylko obecność cookie): ryzyko; mitigacja: walidacja JWT + user context.

## 9. Macierz testów (przypadki)

Legenda:
- Priorytet: P0 (smoke), P1 (ważne), P2 (nice-to-have)
- Typ: M (manual), A (automation candidate)
- Status: Planned/Done/Blocked

| ID | Obszar | Wymaganie / US | Kroki | Oczekiwany rezultat | Priorytet | Typ | Status |
|---|---|---|---|---|---|---|---|
| TP-DB-01 | DB | Healthcheck | GET `/health/db` | 200 + `{ok:true}` | P0 | M/A | Planned |
| TP-DB-02 | DB | Migracje | `python -m alembic upgrade head` na czystej DB | brak błędów, tabele istnieją | P0 | M | Planned |
| TP-AUTH-API-01 | Auth API | Rejestracja | POST `/auth/register` poprawne dane | 200 + `id,email`; rekord w `users` | P0 | M/A | Planned |
| TP-AUTH-API-02 | Auth API | Email unikalny | POST `/auth/register` ponownie ten sam email | 400 | P0 | M/A | Planned |
| TP-AUTH-API-03 | Auth API | Walidacja hasła | POST `/auth/register` hasło <8 lub >19 | 400 | P0 | M/A | Planned |
| TP-AUTH-API-04 | Auth API | Walidacja hasła | hasło bez uppercase | 400 | P1 | M/A | Planned |
| TP-AUTH-API-05 | Auth API | Walidacja hasła | hasło bez cyfry | 400 | P1 | M/A | Planned |
| TP-AUTH-API-06 | Auth API | Walidacja hasła | hasło bez znaku specjalnego | 400 | P1 | M/A | Planned |
| TP-AUTH-API-07 | Auth API | Confirm | `password_confirm != password` | 400 | P1 | M/A | Planned |
| TP-AUTH-API-08 | Auth API | Login | POST `/auth/login` poprawne dane | 200 + token bearer | P0 | M/A | Planned |
| TP-AUTH-API-09 | Auth API | Login błąd | POST `/auth/login` złe hasło/email | 401 | P0 | M/A | Planned |
| TP-AUTH-UI-01 | Auth UI | Register | Wejdź `/register`, podaj poprawne dane, submit | Redirect na `/` + cookie `access_token` | P0 | M | Planned |
| TP-AUTH-UI-02 | Auth UI | Register errors | `/register` hasła różne | Strona zostaje + błąd | P0 | M | Planned |
| TP-AUTH-UI-03 | Auth UI | Register errors | `/register` hasło niespełniające reguł | Strona zostaje + błąd | P0 | M | Planned |
| TP-AUTH-UI-04 | Auth UI | Login | Wejdź `/login`, poprawne dane, submit | Redirect na `/` + cookie `access_token` | P0 | M | Planned |
| TP-AUTH-UI-05 | Auth UI | Login errors | `/login` błędne dane | Strona zostaje + błąd | P0 | M | Planned |
| TP-AUTH-UI-06 | Auth UI | Logout | `POST /logout` (przycisk Wyloguj) | cookie usunięte + redirect | P0 | M | Planned |
| TP-ACCESS-01 | Access | Public pages | GET `/`, `/login`, `/register`, `/forgot-password` | 200 | P1 | M | Planned |
| TP-ACCESS-02 | Access | Protected | GET `/books` bez cookie | Redirect do `/login` | P0 | M | Planned |
| TP-ACCESS-03 | Access | Protected | POST `/books` bez cookie | Redirect do `/login` | P0 | M | Planned |
| TP-SEC-01 | Security | Cookie flags | Po login/register sprawdź cookie | `HttpOnly` + `SameSite=Lax` | P1 | M | Planned |

## 10. Proponowana kolejność realizacji (krok po kroku)
1) Setup DB + env vars
2) Migracje + `/health/db`
3) Smoke: rejestracja/login/logout (UI)
4) Smoke: ochrona `/books`
5) Negatywne scenariusze haseł + duplikat email (API + UI)
6) Security sanity (cookie flags)

## 11. Propozycja automatyzacji (kolejny krok)
Najpierw automatyzować P0:
- `TP-DB-01`
- `TP-AUTH-API-01`, `TP-AUTH-API-02`, `TP-AUTH-API-08`, `TP-AUTH-API-09`
- minimalny test UI można odłożyć (lub zrobić Playwright później)
