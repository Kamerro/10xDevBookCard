# BookCards — DB plan (MVP)

## Założenia (source of truth)

- PostgreSQL
- SQLAlchemy 2.0
- Migracje: Alembic
- Aplikacja: FastAPI (DI dla sesji DB)
- Brak Supabase

## Kluczowe decyzje (z sesji planistycznej)

- PK: UUID we wszystkich tabelach.
- `users.email` jest unikalny.
- `books` mogą się duplikować (brak `unique(user_id, title, author)`).
- Notatki:
  - `notes.id` (UUID) jest przekazywany na frontend i używany do edycji.
  - `notes.number` (int) to stabilny numer notatki per książka (rośnie od 1).
  - Nie uwzględniamy usuwania notatek w MVP.
- Wyniki AI są przechowywane per książka w osobnej tabeli 1:1.
  - `duplicates` i `importance_ranking` przechowujemy w `JSONB`.
  - Status analizy jest przechowywany w DB.
- Usunięcie książki usuwa notatki (FK `ON DELETE CASCADE`).
- Brak usuwania konta w MVP.
- Izolacja danych: `books.user_id` + filtrowanie po user w zapytaniach (bez RLS w MVP).

---

## Schemat

### 1) `users`

**Cel**: przechowanie kont użytkowników (auth: email + hasło) oraz danych potrzebnych do resetu hasła.

**Kolumny**

- `id` UUID PK
- `email` TEXT NOT NULL
- `password_hash` TEXT NOT NULL
- `password_reset_token_hash` TEXT NULL
- `password_reset_token_expires_at` TIMESTAMPTZ NULL
- `created_at` TIMESTAMPTZ NOT NULL

**Constraints / indeksy**

- `unique(email)`
- indeks po `email` (automatycznie wynika z unique, ale w planie uznajemy `unique` jako wystarczające)

**Relacje**

- `users (1) -> books (N)`

---

### 2) `books`

**Cel**: książki użytkownika.

**Kolumny**

- `id` UUID PK
- `user_id` UUID NOT NULL (FK -> `users.id`)
- `title` TEXT NOT NULL
- `author` TEXT NOT NULL
- `created_at` TIMESTAMPTZ NOT NULL

**Constraints / indeksy**

- indeks: `(user_id, created_at)` (lista książek użytkownika)
- indeks: `(user_id, title)` (opcjonalnie; przydatne do listowania/sortowania)

**Relacje**

- `books (1) -> notes (N)`
- `books (1) -> book_ai_analyses (1)`

**Kasowanie**

- FK `books.user_id` bez cascade (brak usuwania userów w MVP)

---

### 3) `notes`

**Cel**: notatki do książki (jedno pole tekstowe), edytowalne.

**Kolumny**

- `id` UUID PK
- `book_id` UUID NOT NULL (FK -> `books.id`)
- `number` INTEGER NOT NULL (unikalny per `book_id`, rosnący od 1)
- `content` TEXT NOT NULL
- `created_at` TIMESTAMPTZ NOT NULL
- `updated_at` TIMESTAMPTZ NOT NULL

**Constraints / indeksy**

- constraint: `unique(book_id, number)`
- indeks: `(book_id, number)`
- indeks: `(book_id, updated_at)` (pod edycję / sortowanie)

**Kasowanie**

- FK `notes.book_id` z `ON DELETE CASCADE`

---

### 4) `book_ai_analyses`

**Cel**: zapis wyników AI per książka + status przetwarzania.

**Kolumny**

- `id` UUID PK
- `book_id` UUID NOT NULL (FK -> `books.id`)
- `analysis_status` TEXT NOT NULL
- `summary` TEXT NULL
- `duplicates` JSONB NOT NULL
- `importance_ranking` JSONB NOT NULL
- `analyzed_at` TIMESTAMPTZ NULL
- `analysis_error` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL
- `updated_at` TIMESTAMPTZ NOT NULL

**Constraints / indeksy**

- constraint: `unique(book_id)` (wymusza relację 1:1)
- indeks: `(analysis_status)` (opcjonalnie; pod joby/monitoring)

**Uwagi**

- `duplicates` i `importance_ranking` jako `JSONB` trzymają listy (`list[str]`, `list[int]`).
- `analysis_status` w MVP może być stringiem; enum można dodać później, jeśli będzie potrzeba.

---

## Zasady integralności danych

- Każdy `book` musi należeć do `user`.
- Każda `note` musi należeć do `book`.
- Każda analiza AI (jeśli istnieje) należy do `book` i jest co najwyżej jedna per book.

## Zasady bezpieczeństwa (MVP)

- Brak RLS.
- Bezpieczeństwo realizowane w warstwie aplikacji:
  - Wszystkie zapytania do `books/notes/book_ai_analyses` muszą być filtrowane po `user_id` właściciela.

## Wskazówki implementacyjne (SQLAlchemy / Alembic)

- Modele w `app/models` bez logiki biznesowej.
- Relacje SQLAlchemy jawne, typowane (`Mapped[...]`).
- Migracje generowane i utrzymywane przez Alembic, bez runtime schema changes.
