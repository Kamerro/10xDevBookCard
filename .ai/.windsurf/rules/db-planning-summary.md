# BookCards — DB planning summary (MVP)

## Kontekst

- Stack (source of truth): PostgreSQL + SQLAlchemy 2.0 + Alembic + FastAPI.
- Cel: zaplanować schemat bazy danych dla MVP zgodnie z PRD.
- Bez Supabase.

## Główne encje (MVP)

- Users
- Books
- Notes
- Book AI analysis (wynik AI per książka)

## Decyzje

### Identyfikatory

- PK: UUID (dla wszystkich tabel).
- `notes.id` (UUID) będzie przekazywany na frontend i używany do identyfikacji notatki przy edycji.

### Users

- `users.email`: unikalny.
- Auth: email + hasło.
- Hasła: przechowywany wyłącznie `password_hash` (bcrypt).
- Reset hasła: token wysyłany emailowo — planujemy pola w DB na hash tokenu + czas wygaśnięcia.
- Usuwanie konta użytkownika: poza zakresem MVP.

### Books

- Minimalne pola biznesowe: `title`, `author`.
- Duplikaty książek dozwolone (np. różne tłumaczenia), brak constraint typu `unique(user_id, title, author)`.
- Relacja: `users (1) -> books (N)`.

### Notes

- Minimalne pole biznesowe: `content` (jedno pole tekstowe).
- Edycja notatki: przez `notes.id` (UUID).
- Usuwanie notatek: nie uwzględniamy w MVP.
- Relacja: `books (1) -> notes (N)`.

### AI (analiza notatek per książka)

- Osobna tabela 1:1 per book (np. `book_ai_analyses`).
- Wyniki AI przechowywane w DB.
- `duplicates` oraz `importance_ranking` przechowujemy jako `JSONB`.
- Potrzebne statusy:
  - `analysis_status` (np. `pending|processing|done|failed`)
  - `analyzed_at`
  - `analysis_error`

### Kasowanie

- Usunięcie książki usuwa notatki (PRD).
- Rekomendacja MVP: FK z `ON DELETE CASCADE` dla `notes.book_id`.

### Izolacja danych

- Każdy użytkownik widzi tylko swoje dane.
- Izolacja na poziomie schematu: `books.user_id` i wszystkie zapytania filtrowane po user.
- RLS: nie w MVP.

## Otwarta decyzja (do domknięcia)

Reguła AI (`app/services/ai_service.py` rules) zakłada `importance_ranking: list[int]`.

Dlatego potrzebujemy stabilnego, numerycznego identyfikatora notatki w ramach książki.

- Propozycja: `notes.number` (int), rosnący per `book_id`, constraint `unique(book_id, number)`.
- Alternatywa (odradzana przy obecnych regułach): ranking po UUID wymagałby zmiany kontraktu AI.

## Ryzyka / uwagi

- Brak usuwania notatek upraszcza stabilność `notes.number` i rankingów.
- JSONB jest wystarczające na MVP; przy rozbudowie można przenieść dane do osobnych tabel.
