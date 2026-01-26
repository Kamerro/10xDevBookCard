# Plan implementacji — POST /books/{book_id}/notes (MVP)

## Cel

Dodać pojedynczą notatkę do książki. Jeżeli po dodaniu książka ma >= 3 notatki, uruchomić AI w `BackgroundTasks` (bez blokowania requestu).

## Kontrakt (z `.windsurf/rules/api-plan.md`)

### Path

- `book_id: UUID`

### Request

- `content: str`

### Response (200)

- `id: UUID`
- `book_id: UUID`
- `number: int`
- `content: str`
- `created_at: datetime`
- `updated_at: datetime`

### Błędy

- `401` brak/niepoprawny token
- `404` jeśli książka nie należy do usera lub nie istnieje

## Założenia DB (z `.windsurf/rules/db-plan.md`)

- `notes.number` rośnie od 1 per `book_id`.
- `unique(book_id, number)`.
- Brak usuwania notatek.

## Warstwy

- `app/api`: walidacja + DI (`db`, `current_user`, `BackgroundTasks`).
- `app/services`:
  - tworzenie notatki
  - wyliczanie `number`
  - decyzja o triggerze AI (>=3)
  - uruchomienie background task

## Kroki implementacji (high-level)

### 1) Modele

- `Book` model (minimum: `id`, `user_id`, `title`, `author`, `created_at`).
- `Note` model (`id`, `book_id`, `number`, `content`, `created_at`, `updated_at`).

### 2) Schematy Pydantic

- `CreateNoteRequest` (`content`)
- `NoteOut`

### 3) Auth dependency

- Dodać `get_current_user` dependency (JWT) w `app/api/deps.py` albo `app/api/auth_deps.py`.

### 4) Serwis notes

- `app/services/notes_service.py`:
  - `create_note(db: Session, *, user_id: UUID, book_id: UUID, content: str) -> Note`
    - sprawdź, czy book istnieje i należy do usera
    - wylicz `next_number`:
      - `select(max(Note.number)) where Note.book_id == book_id`
      - `next_number = (max or 0) + 1`
    - utwórz note
    - `db.add/commit/refresh`

### 5) Trigger AI (BackgroundTasks)

- W `notes_service.create_note` lub osobnej funkcji:
  - policz liczbę notatek per book (po commicie)
  - jeśli >= 3:
    - zapewnij istnienie rekordu 1:1 `BookAIAnalysis` dla książki (jeśli brak: utwórz)
    - ustaw `analysis_status` na `processing` (lub `pending` -> `processing`)
    - dodać background task `ai_service.analyze_book(book_id=...)`

Uwaga: AI ma być wyłącznie w background task (rules). Sama implementacja AI poza zakresem tego planu, ale plan zakłada istnienie funkcji w `app/services/ai_service.py` oraz aktualizację rekordu analizy do `done`/`failed`.

### 6) Endpoint

- `POST /books/{book_id}/notes` w `app/api/notes.py` (lub `books.py` — ale zgodnie z API plan: notes route pod books).
- Parametry:
  - `book_id` path
  - `payload: CreateNoteRequest`
  - `db: Session = Depends(get_db)`
  - `current_user = Depends(get_current_user)`
  - `background_tasks: BackgroundTasks`
- Zwrócić `NoteOut`.

## Obsługa błędów

- Book nie istnieje / nie należy do usera:
  - `HTTPException(404)`
- Brak auth:
  - `HTTPException(401)`

## Testy (minimalne, później)

- dodanie notatki do własnej książki -> 200
- dodanie do cudzej książki -> 404
- po trzeciej notatce: wywołanie background task (mock)

## Workflow 3×3 (proponowana iteracja)

### Iteracja 1 (3 kroki)

1. Dodać modele `Book`, `Note`.
2. Dodać schematy Pydantic notes.
3. Dodać `notes_service.create_note` (bez AI trigger).

### Iteracja 2 (3 kroki)

1. Dodać JWT dependency `get_current_user`.
2. Dodać endpoint `POST /books/{book_id}/notes`.
3. Dodać wyliczanie `number` + constraint.

### Iteracja 3 (3 kroki)

1. Dodać trigger BackgroundTasks po >=3 notatkach.
2. Dodać testy z mockiem.
3. Wygenerować `curl`.
