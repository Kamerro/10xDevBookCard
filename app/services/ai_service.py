from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.session import SessionLocal
from app.models.book import Book
from app.models.book_ai_analysis import BookAIAnalysis
from app.services.openrouter_service import (
    OpenRouterError,
    structured_output,
)


SCHEMA_NAME = "book_ai_analysis_v1"

JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "duplicates", "importance_ranking"],
    "properties": {
        "summary": {"type": "string", "minLength": 1},
        "duplicates": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["note_numbers", "reason"],
                "properties": {
                    "note_numbers": {
                        "type": "array",
                        "minItems": 2,
                        "items": {"type": "integer", "minimum": 1},
                    },
                    "reason": {"type": "string", "minLength": 1},
                },
            },
        },
        "importance_ranking": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["note_number", "score", "reason"],
                "properties": {
                    "note_number": {"type": "integer", "minimum": 1},
                    "score": {"type": "integer", "minimum": 1, "maximum": 10},
                    "reason": {"type": "string", "minLength": 1},
                },
            },
        },
    },
}


def _get_book_for_user(db: Session, *, book_id: UUID, user_id: UUID) -> Book | None:
    return db.execute(select(Book).where(Book.id == book_id, Book.user_id == user_id)).scalar_one_or_none()


def _get_or_create_ai_row(db: Session, *, book_id: UUID) -> BookAIAnalysis:
    ai = db.execute(select(BookAIAnalysis).where(BookAIAnalysis.book_id == book_id)).scalar_one_or_none()
    if ai is None:
        ai = BookAIAnalysis(
            book_id=book_id,
            analysis_status="pending",
            analysis_version=0,
            requested_version=0,
            summary=None,
            duplicates=[],
            importance_ranking=[],
            analyzed_at=None,
            analysis_error=None,
        )
        db.add(ai)
        db.commit()
        db.refresh(ai)
    return ai


def trigger_analysis_if_needed(
    db: Session,
    *,
    book_id: UUID,
    user_id: UUID,
    note_count: int,
    background_tasks: BackgroundTasks,
) -> None:
    if note_count < 3:
        return

    if not settings.openrouter_api_key:
        return

    book = _get_book_for_user(db, book_id=book_id, user_id=user_id)
    if book is None:
        return

    ai = _get_or_create_ai_row(db, book_id=book_id)

    ai.requested_version += 1

    should_schedule = ai.analysis_status != "processing"
    if should_schedule:
        ai.analysis_status = "processing"
        ai.analysis_error = None

    db.commit()

    if should_schedule:
        background_tasks.add_task(analyze_book_task, book_id=book_id, user_id=user_id)


async def analyze_book_task(*, book_id: UUID, user_id: UUID) -> None:
    db = SessionLocal()
    try:
        await analyze_book(db, book_id=book_id, user_id=user_id)
    finally:
        db.close()


async def analyze_book(db: Session, *, book_id: UUID, user_id: UUID) -> None:
    book = _get_book_for_user(db, book_id=book_id, user_id=user_id)
    if book is None:
        return

    notes = list(book.notes)
    if len(notes) < 3:
        return

    ai = _get_or_create_ai_row(db, book_id=book_id)

    max_reruns = 2
    reruns = 0

    while True:
        db.refresh(ai)
        target_version = ai.requested_version

        if ai.analysis_status != "processing":
            ai.analysis_status = "processing"
            ai.analysis_error = None
            db.commit()

        notes_sorted = sorted(notes, key=lambda n: n.number)
        notes_lines = "\n".join([f"{n.number}: {n.content}" for n in notes_sorted])

        messages = [
            {
                "role": "system",
                "content": (
                    "Jesteś asystentem, który analizuje notatki do książki. "
                    "Zwracasz WYŁĄCZNIE JSON zgodny ze schematem. "
                    "Nie dodawaj żadnego tekstu poza JSON. "
                    "Jeśli informacji jest za mało, nadal zwróć poprawny JSON i zrób rozsądne, ostrożne wnioski."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Tytuł: {book.title}\n"
                    f"Autor: {book.author}\n\n"
                    "Notatki (number: content):\n"
                    f"{notes_lines}\n\n"
                    "Zadanie:\n"
                    "1) Napisz summary.\n"
                    "2) Wykryj duplikaty znaczeniowe i podaj grupy note_numbers.\n"
                    "3) Oceń ważność każdej notatki (1-10) i podaj importance_ranking."
                ),
            },
        ]

        try:
            result = await structured_output(
                messages=messages,
                schema_name=SCHEMA_NAME,
                json_schema=JSON_SCHEMA,
            )
        except OpenRouterError as exc:
            ai.analysis_status = "failed"
            ai.analysis_error = str(exc)
            db.commit()
            return
        except Exception as exc:
            ai.analysis_status = "failed"
            ai.analysis_error = "unexpected_error"
            db.commit()
            return

        db.refresh(ai)
        if ai.requested_version != target_version:
            reruns += 1
            if reruns > max_reruns:
                ai.analysis_status = "failed"
                ai.analysis_error = "too_many_reruns"
                db.commit()
                return
            continue

        ai.summary = str(result["summary"]).strip()
        ai.duplicates = result["duplicates"]
        ai.importance_ranking = result["importance_ranking"]
        ai.analyzed_at = datetime.now(timezone.utc)
        ai.analysis_error = None
        ai.analysis_status = "ready"
        ai.analysis_version = target_version
        db.commit()
        return
