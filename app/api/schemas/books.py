from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BookCreateRequest(BaseModel):
    title: str
    author: str


class BookOut(BaseModel):
    id: UUID
    title: str
    author: str
    created_at: datetime


class BookListOut(BaseModel):
    id: UUID
    title: str
    author: str
    created_at: datetime
    ai_status: str


class NoteOut(BaseModel):
    id: UUID
    book_id: UUID
    number: int
    content: str
    created_at: datetime
    updated_at: datetime


class BookAIAnalysisOut(BaseModel):
    status: str
    summary: str | None
    duplicates: list
    importance_ranking: list
    analyzed_at: datetime | None
    error: str | None


class BookDetailOut(BaseModel):
    id: UUID
    title: str
    author: str
    created_at: datetime
    notes: list[NoteOut]
    ai: BookAIAnalysisOut | None


class OkResponse(BaseModel):
    ok: bool = True
