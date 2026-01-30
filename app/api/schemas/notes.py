from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NoteCreateRequest(BaseModel):
    content: str


class NoteUpdateRequest(BaseModel):
    content: str


class NoteOut(BaseModel):
    id: UUID
    book_id: UUID
    number: int
    content: str
    created_at: datetime
    updated_at: datetime
