from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.book import Book
from app.models.book_ai_analysis import BookAIAnalysis
from app.models.note import Note


def create_book(db: Session, *, user_id: UUID, title: str, author: str) -> Book:
    book = Book(user_id=user_id, title=title, author=author)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_user_books(db: Session, *, user_id: UUID) -> list[Book]:
    stmt = (
        select(Book)
        .where(Book.user_id == user_id)
        .outerjoin(BookAIAnalysis)
        .options(joinedload(Book.ai_analysis))
        .order_by(Book.created_at.desc())
    )
    return list(db.execute(stmt).scalars().unique().all())


def get_book_by_id(db: Session, *, book_id: UUID, user_id: UUID) -> Book | None:
    stmt = (
        select(Book)
        .where(Book.id == book_id, Book.user_id == user_id)
        .options(
            joinedload(Book.notes),
            joinedload(Book.ai_analysis),
        )
    )
    return db.execute(stmt).scalars().unique().one_or_none()


def delete_book(db: Session, *, book_id: UUID, user_id: UUID) -> bool:
    book = db.execute(
        select(Book).where(Book.id == book_id, Book.user_id == user_id)
    ).scalar_one_or_none()
    if book is None:
        return False
    db.delete(book)
    db.commit()
    return True


def get_book_ai_status(book: Book) -> str:
    if book.ai_analysis is None:
        return "pending"
    return book.ai_analysis.analysis_status
