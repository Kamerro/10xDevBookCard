from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.schemas.notes import NoteOut, NoteUpdateRequest
from app.models.user import User
from app.services.ai_service import trigger_analysis_if_needed
from app.services.note_service import count_notes_for_book, get_note_by_id, update_note

router = APIRouter(prefix="/notes", tags=["notes"])


@router.put("/{note_id}", response_model=NoteOut)
async def update_note_endpoint(
    note_id: UUID,
    payload: NoteUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteOut:
    note = get_note_by_id(db, note_id=note_id, user_id=current_user.id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    note = update_note(db, note=note, content=payload.content)

    note_count = count_notes_for_book(db, book_id=note.book_id)
    trigger_analysis_if_needed(
        db,
        book_id=note.book_id,
        user_id=current_user.id,
        note_count=note_count,
        background_tasks=background_tasks,
    )

    return NoteOut(
        id=note.id,
        book_id=note.book_id,
        number=note.number,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )
