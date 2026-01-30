# Auth UI (MVP) -> implementacja produkcyjna (checklista)

## Co trzeba zmienić w produkcji

## 1) Oddzielenie UI routes od API

- `POST /login` w `app/web` powinien:
  - przyjąć dane z formularza (`email`, `password`) jako `Form(...)`.
  - wywołać logikę autoryzacji (bezpośrednio w serwisie lub przez API layer), zamiast ślepego redirectu.
- Alternatywnie:
  - UI `POST /login` może wywoływać `POST /api/auth/login` (wewnętrznie), a potem ustawiać cookie.

## 2) Prawdziwa autoryzacja i sesja

- JSON API endpoint `POST /api/auth/login` (JWT) oraz `POST /api/auth/register`.
- UI (SSR) przechowuje sesję jako cookie `HttpOnly` (`access_token`).
- Dodać `logout`:
  - UI link w headerze powinien być akcją (np. `POST /logout`) czyszczącą cookie.

## 3) Ochrona routów

- Strony wymagające logowania (np. `/books`) muszą sprawdzać sesję (dependency w routerze web):
  - brak sesji -> redirect do `/login`.
- Dodać mechanizm „return_to”:
  - po udanym logowaniu redirect do pierwotnie żądanego URL.

## 4) Walidacja i błędy UX

- Login:
  - błędne dane -> render tej samej strony z komunikatem (np. `error_login`).
- Rejestracja:
  - walidacja: email, min. długość hasła, zgodność `password` i `password_confirm`.
  - błędy -> render `register.html` z komunikatami.
- Forgot password:
  - komunikat zawsze neutralny („Jeśli konto istnieje, wyślemy email”), aby nie ujawniać istnienia kont.

## 5) Reset hasła (flow)

- Dodać widok: `GET /reset-password?token=...` + formularz `POST /reset-password`.
- Backend:
  - generacja tokenu resetu, TTL, zapis w DB, wysyłka maila.
  - wymuszenie jednorazowości tokenu.

## 6) Bezpieczeństwo

- CSRF dla formularzy, jeśli używamy cookie auth (zalecane).
- Rate limiting dla logowania i resetu hasła.
- Nagłówki bezpieczeństwa (CSP, HSTS w prod).
- Nie logować haseł / danych wrażliwych.

## 7) Porządek w plikach

- Dodać brakujące pliki zależności (`requirements.txt` albo `pyproject.toml`).
- Dodać testy minimalne:
  - login success/fail (API)
  - register success/duplicate
  - reset request neutral response
