from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.schemas.books import (
    BookAIAnalysisOut,
    BookCreateRequest,
    BookDetailOut,
    BookListOut,
    BookOut,
    NoteOut,
    OkResponse,
)
from app.api.schemas.notes import NoteCreateRequest
from app.api.schemas.notes import NoteOut as NoteOutSchema
from app.models.user import User
from app.services.book_service import (
    create_book,
    delete_book,
    get_book_ai_status,
    get_book_by_id,
    get_user_books,
)
from app.services.note_service import create_note, get_book_for_user, count_notes_for_book
from app.services.ai_service import trigger_analysis_if_needed

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
async def create_book_endpoint(
    payload: BookCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookOut:
    book = create_book(db, user_id=current_user.id, title=payload.title, author=payload.author)
    return BookOut(
        id=book.id,
        title=book.title,
        author=book.author,
        created_at=book.created_at,
    )


@router.get("", response_model=list[BookListOut])
async def list_books_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BookListOut]:
    books = get_user_books(db, user_id=current_user.id)
    return [
        BookListOut(
            id=book.id,
            title=book.title,
            author=book.author,
            created_at=book.created_at,
            ai_status=get_book_ai_status(book),
        )
        for book in books
    ]


@router.get("/{book_id}", response_model=BookDetailOut)
async def get_book_endpoint(
    book_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookDetailOut:
    book = get_book_by_id(db, book_id=book_id, user_id=current_user.id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    notes_out = [
        NoteOut(
            id=note.id,
            book_id=note.book_id,
            number=note.number,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
        for note in sorted(book.notes, key=lambda n: n.number)
    ]

    ai_out = None
    if book.ai_analysis is not None:
        ai_out = BookAIAnalysisOut(
            status=book.ai_analysis.analysis_status,
            summary=book.ai_analysis.summary,
            duplicates=book.ai_analysis.duplicates,
            importance_ranking=book.ai_analysis.importance_ranking,
            analyzed_at=book.ai_analysis.analyzed_at,
            error=book.ai_analysis.analysis_error,
        )

    return BookDetailOut(
        id=book.id,
        title=book.title,
        author=book.author,
        created_at=book.created_at,
        notes=notes_out,
        ai=ai_out,
    )


@router.delete("/{book_id}", response_model=OkResponse)
async def delete_book_endpoint(
    book_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OkResponse:
    deleted = delete_book(db, book_id=book_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return OkResponse(ok=True)


@router.post(
    "/{book_id}/notes",
    response_model=NoteOutSchema,
    status_code=status.HTTP_201_CREATED,
    tags=["notes"],
)
async def create_note_endpoint(
    book_id: UUID,
    payload: NoteCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteOutSchema:
    book = get_book_for_user(db, book_id=book_id, user_id=current_user.id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    note = create_note(db, book_id=book_id, content=payload.content)

    note_count = count_notes_for_book(db, book_id=book_id)
    trigger_analysis_if_needed(
        db,
        book_id=book_id,
        user_id=current_user.id,
        note_count=note_count,
        background_tasks=background_tasks,
    )

    return NoteOutSchema(
        id=note.id,
        book_id=note.book_id,
        number=note.number,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )
