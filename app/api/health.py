from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/db")
def health_db(db: Session = Depends(get_db)) -> dict:
    db.execute(text("select 1"))
    return {"ok": True}
