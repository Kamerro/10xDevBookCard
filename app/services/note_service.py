from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.note import Note


def get_next_note_number(db: Session, *, book_id: UUID) -> int:
    result = db.execute(select(func.coalesce(func.max(Note.number), 0)).where(Note.book_id == book_id)).scalar()
    return result + 1


def create_note(db: Session, *, book_id: UUID, content: str) -> Note:
    number = get_next_note_number(db, book_id=book_id)
    note = Note(book_id=book_id, number=number, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_note_by_id(db: Session, *, note_id: UUID, user_id: UUID) -> Note | None:
    stmt = select(Note).join(Book).where(Note.id == note_id, Book.user_id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def update_note(db: Session, *, note: Note, content: str) -> Note:
    note.content = content
    db.commit()
    db.refresh(note)
    return note


def get_book_for_user(db: Session, *, book_id: UUID, user_id: UUID) -> Book | None:
    stmt = select(Book).where(Book.id == book_id, Book.user_id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def count_notes_for_book(db: Session, *, book_id: UUID) -> int:
    result = db.execute(select(func.count()).select_from(Note).where(Note.book_id == book_id)).scalar()
    return result or 0
