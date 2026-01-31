# PRD – BookCards (MVP)

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](../03-governance/governance.md)
> - [PRD](./prd.md)

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

#### Dostęp i widoczność (wpływ uwierzytelniania na UI)

- Strony publiczne (dostępne bez logowania):
  - Strona główna (landing)
  - Logowanie
  - Rejestracja
  - Odzyskiwanie hasła / reset hasła
- Strony wymagające zalogowania:
  - Lista książek użytkownika
  - Widok książki + notatki
  - Dodawanie / edycja notatek
  - (Docelowo) widoki związane z analizą AI
- Header powinien zawsze komunikować stan użytkownika:
  - niezalogowany: akcje „Logowanie”, „Rejestracja”
  - zalogowany: informacja o użytkowniku (np. email) + akcja „Wyloguj”
- Przekierowania:
  - próba wejścia na stronę chronioną bez logowania -> przekierowanie do logowania
  - po poprawnym logowaniu -> przekierowanie na stronę główną lub poprzednio żądaną stronę

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

### US-01a Walidacja rejestracji
Jako nowy użytkownik  
Chcę otrzymać czytelny komunikat błędu, gdy email jest zajęty lub hasło jest zbyt słabe  
Aby szybko poprawić dane i założyć konto

### US-01b Potwierdzenie hasła
Jako nowy użytkownik  
Chcę potwierdzić hasło podczas rejestracji  
Aby uniknąć literówek i późniejszych problemów z logowaniem

### US-02 Logowanie
Jako użytkownik  
Chcę zalogować się do systemu przy użyciu emaila i hasła  
Aby mieć dostęp do moich danych

### US-02a Błąd logowania
Jako użytkownik  
Chcę otrzymać informację o błędnym emailu lub haśle  
Aby móc poprawić dane logowania

### US-03 Wylogowanie
Jako zalogowany użytkownik  
Chcę móc się wylogować  
Aby zakończyć sesję na współdzielonym komputerze

### US-04 Odzyskiwanie hasła (żądanie)
Jako użytkownik, który nie pamięta hasła  
Chcę poprosić o link do resetu hasła  
Aby odzyskać dostęp do konta

### US-04a Reset hasła (ustawienie nowego)
Jako użytkownik  
Chcę ustawić nowe hasło za pomocą linku z emaila  
Aby ponownie zalogować się do konta

### US-05 Kontrola dostępu do danych
Jako użytkownik  
Chcę mieć pewność, że widzę tylko swoje książki i notatki  
Aby moje dane były prywatne

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

### US-06 Widoczność statusu użytkownika
Jako użytkownik  
Chcę widzieć w interfejsie, czy jestem zalogowany oraz móc szybko przejść do logowania/rejestracji  
Aby łatwo poruszać się po aplikacji i rozumieć, dlaczego część funkcji jest niedostępna

### US-07 Przekierowanie po logowaniu
Jako użytkownik  
Chcę po zalogowaniu wrócić do strony, którą próbowałem otworzyć  
Aby nie tracić kontekstu i czasu

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

## 11: Kolekcje reguł
- Tytuł: Kolekcje reguł
- Opis: Jako użytkownik chcę móc zapisywać i edytować zestawy reguł, aby szybko wykorzystywać sprawdzone rozwiązania w różnych projektach.
- Kryteria akceptacji:
  - Użytkownik może zapisać aktualny zestaw reguł jako kolekcję (nazwa, opis, reguły).
  - Użytkownik może aktualizować kolekcję.
  - Użytkownik może usunąć kolekcję.
  - Użytkownik może przywrócić kolekcję do poprzedniej wersji (pending changes).
  - Funkcjonalność kolekcji nie jest dostępna bez logowania się do systemu (12).

## 12: Bezpieczny dostęp i uwierzytelnianie

- Tytuł: Bezpieczny dostęp
- Opis: Jako użytkownik chcę mieć możliwość rejestracji i logowania się do systemu w sposób zapewniający bezpieczeństwo moich danych.
- Kryteria akceptacji:
  - Logowanie i rejestracja odbywają się na dedykowanych stronach.
  - Logowanie wymaga podania adresu email i hasła.
  - Rejestracja wymaga podania adresu email, hasła i potwierdzenia hasła.
  - Użytkownik MOŻE korzystać z tworzenia reguł "ad-hoc" bez logowania się do systemu (US-001).
  - Użytkownik NIE MOŻE korzystać z funkcji Kolekcji bez logowania się do systemu (US-003).
  - Użytkownik może logować się do systemu poprzez przycisk w prawym górnym rogu.
  - Użytkownik może się wylogować z systemu poprzez przycisk w prawym górnym rogu w głównym Layout
  - Nie korzystamy z zewnętrznych serwisów logowania (np. Google, GitHub).
  - Odzyskiwanie hasła powinno być możliwe.
