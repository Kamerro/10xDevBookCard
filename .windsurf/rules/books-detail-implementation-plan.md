# Plan implementacji — GET /api/books/{book_id} (MVP)

## Cel

Zwrócić szczegóły książki należącej do zalogowanego użytkownika, wraz z notatkami oraz (opcjonalnie) statusem/wynikiem analizy AI.

## Kontrakt (z `.windsurf/rules/api-plan.md`)

### Path

- `book_id: UUID`

### Response (200)

- `id: UUID`
- `title: str`
- `author: str`
- `created_at: datetime`
- `notes: list[NoteOut]`
- `ai: BookAIAnalysisOut | None`

### Błędy

- `401` brak/niepoprawny token
- `404` jeśli książka nie należy do usera lub nie istnieje

## Warstwy

- `app/api`: HTTP + DI
- `app/services`: odczyt danych (book + notes + analysis) i mapowanie do prostych struktur
- `app/models`: SQLAlchemy modele

## Kroki implementacji (high-level)

### 1) Modele

- `Book`, `Note`, `BookAIAnalysis` zgodnie z `.windsurf/rules/db-plan.md`.

### 2) Schematy Pydantic

- `NoteOut` (już wspólne dla notes)
- `BookAIAnalysisOut`:
  - `analysis_status: str`
  - `summary: str | None`
  - `duplicates: list[str]`
  - `importance_ranking: list[int]`
  - `analyzed_at: datetime | None`
- `BookDetailOut`

Uwaga: `duplicates` i `importance_ranking` w DB są JSONB; w API wystawiamy je jako listy.

### 3) Serwis books

- Implementacja jest w `app/services/book_service.py`:
  - `get_book_by_id(db, *, book_id, user_id)` + eager load relacji `notes` i `ai_analysis`
  - sortowanie notatek po `number` w warstwie API (albo w serwisie)

Uwagi

- Jeśli rekord analizy AI nie istnieje, w response zwracamy `ai = null`.

### 4) Endpoint

- `GET /api/books/{book_id}` w `app/api/books.py` (router jest mountowany pod `/api` w `app/main.py`):
  - `db = Depends(get_db)`
  - `current_user = Depends(get_current_user)`
  - zwróć `BookDetailOut`

## Obsługa błędów

- Jeśli book nie istnieje lub nie należy do usera -> `404`.

## Testy (minimalne, później)

- Pobranie własnej książki -> 200
- Pobranie cudzej -> 404
- Bez tokena -> 401

## Workflow 3×3 (proponowana iteracja)

### Iteracja 1 (3 kroki)

1. Dodać model `BookAIAnalysis` + relację 1:1.
2. Dodać Pydantic schematy `BookAIAnalysisOut` i `BookDetailOut`.
3. Dodać `books_service.get_book_detail` (bez optymalizacji).

### Iteracja 2 (3 kroki)

1. Dodać endpoint `GET /books/{book_id}`.
2. Dodać mapowanie JSONB -> list w response.
3. Dodać testy.
