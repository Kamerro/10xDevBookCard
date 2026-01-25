# PRD – BookCards (MVP)

## 1. Overview produktu

BookCards to prywatna aplikacja webowa umożliwiająca użytkownikom budowanie osobistej biblioteki książek oraz dodawanie notatek w trakcie czytania.  
Aplikacja automatycznie analizuje notatki przy użyciu AI, aby streszczać treści, wykrywać powtarzające się informacje oraz określać względną ważność notatek.

Produkt kładzie nacisk na:
- maksymalnie prosty i czytelny interfejs
- minimalną liczbę interakcji
- brak konieczności ręcznego porządkowania wiedzy

---

## 2. Problem użytkownika

Osoby czytające książki często robią notatki, które:
- są chaotyczne,
- powtarzają te same informacje,
- szybko tracą na użyteczności po zakończeniu lektury.

Brakuje prostego narzędzia, które pozwala:
- gromadzić notatki per książka,
- automatycznie wyciągać z nich esencję,
- oceniać, które informacje są najważniejsze,
bez konieczności ręcznej organizacji treści.

---

## 3. Cele produktu

### Cele biznesowe
- Dostarczenie działającego MVP aplikacji webowej
- Weryfikacja użyteczności automatycznej analizy notatek przez AI

### Cele użytkownika
- Szybkie dodawanie książek i notatek
- Brak opóźnień i skomplikowanej obsługi
- Automatyczna analiza notatek bez dodatkowych decyzji

---

## 4. Zakres MVP

### 4.1 Funkcjonalności wchodzące w zakres MVP

#### Autoryzacja
- Rejestracja użytkownika (email + hasło)
- Logowanie
- Reset hasła przez email
- Każdy użytkownik ma dostęp wyłącznie do własnych danych

#### Książki
- Dodawanie książki (minimum: tytuł, autor)
- Wyświetlanie listy książek użytkownika
- Usuwanie książki (wraz z notatkami)

#### Notatki
- Dodawanie jednej notatki na raz
- Jedna notatka = jedno pole tekstowe
- Możliwość edycji i nadpisywania notatki
- Jedna książka może zawierać wiele notatek
- Notatki prezentowane w formie estetycznych „fiszek”

#### AI – analiza notatek
- AI działa **per książka**
- Uruchamiane automatycznie po dodaniu notatki
- AI aktywuje się dopiero po osiągnięciu minimum **3 notatek dla książki**
- Przetwarzanie odbywa się asynchronicznie (background task)
- AI:
  - streszcza treści notatek
  - wykrywa wspólne / powtarzające się informacje
  - ocenia ważność każdej notatki
  - numeruje notatki względem istotności
- Wyniki AI są zapisywane w bazie danych
- Użytkownik widzi informację o nowym stanie analizy (np. badge / ikona)

---

## 5. Poza zakresem MVP (świadomie wykluczone)

- Tagowanie i kategoryzacja notatek
- Wyszukiwarka
- Ręczna edycja wyników AI
- Konfiguracja promptów AI
- Eksport danych
- Funkcje społecznościowe i współdzielenie
- Integracje zewnętrzne (Goodreads, Kindle, itp.)
- Import plików (PDF, EPUB)
- Aplikacja mobilna

---

## 6. User Stories

### US-01 Rejestracja
Jako nowy użytkownik  
Chcę założyć konto przy użyciu emaila  
Aby mieć prywatny dostęp do swoich książek i notatek

### US-02 Dodanie książki
Jako zalogowany użytkownik  
Chcę dodać książkę  
Aby móc przypisywać do niej notatki

### US-03 Dodanie notatki
Jako użytkownik  
Chcę dodać pojedynczą notatkę do książki  
Aby zapisać ważną informację z lektury

### US-04 Automatyczna analiza AI
Jako użytkownik  
Chcę, aby AI automatycznie analizowało moje notatki  
Aby bez wysiłku otrzymać streszczenie i ocenę ważności treści

### US-05 Przegląd wyników
Jako użytkownik  
Chcę widzieć uporządkowane notatki i ich ważność  
Aby szybko zrozumieć kluczowe idee książki

---

## 7. Kryteria sukcesu

- Użytkownik bez instrukcji potrafi:
  - założyć konto
  - dodać książkę
  - dodać notatki
  - zobaczyć efekt działania AI
- Brak odczuwalnych opóźnień w interfejsie
- AI działa automatycznie i przewidywalnie
- Dane są trwale zapisywane w bazie
- Interfejs jest czytelny i minimalistyczny

---

## 8. Wymagania niefunkcjonalne

- Asynchroniczne przetwarzanie AI
- Brak blokowania requestów użytkownika
- Podstawowe zabezpieczenia aplikacji
- Obsługa wielu użytkowników
- Stabilne działanie w niskiej skali (MVP)

---

## 9. Stack technologiczny (referencja)

- Backend: FastAPI (Python)
- Baza danych: PostgreSQL
- AI: zewnętrzne API (LLM)
- Hosting: Fly.io
- Konteneryzacja: Docker
- CI: GitHub Actions

---

## 10. Status dokumentu
- Wersja: 1.0
- Zakres: MVP
- Dokument stanowi główne źródło kontekstu dla AI podczas implementacji projektu
