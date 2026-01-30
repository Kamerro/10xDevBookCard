from __future__ import annotations

from uuid import UUID

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.settings import settings
from app.models.user import User
from app.services.book_service import (
    create_book as create_book_service,
    delete_book as delete_book_service,
    get_book_by_id,
    get_user_books,
)
from app.services.note_service import (
    count_notes_for_book,
    create_note as create_note_service,
    get_note_by_id,
    update_note as update_note_service,
)
from app.services.ai_service import trigger_analysis_if_needed

templates = Jinja2Templates(directory="templates")

router = APIRouter()


def get_current_user_from_cookie(request: Request, db: Session) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        from sqlalchemy import select
        user = db.execute(select(User).where(User.id == UUID(user_id_str))).scalar_one_or_none()
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        return None


def _require_auth(request: Request) -> Response | None:
    if not request.cookies.get("access_token"):
        return RedirectResponse(url="/login", status_code=303)
    return None


@router.get("/books", response_class=HTMLResponse)
async def books_index(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    
    user = get_current_user_from_cookie(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    
    books = get_user_books(db, user_id=user.id)
    context = {
        "request": request,
        "books": books,
        "selected_book": None,
        "notes": [],
        "edit_note_id": None,
        "error_add_book": None,
    }
    return templates.TemplateResponse("books/index.html", context)


@router.get("/books/{book_id}", response_class=HTMLResponse)
async def books_detail(request: Request, book_id: str, db: Session = Depends(get_db)) -> HTMLResponse:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    
    user = get_current_user_from_cookie(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        return RedirectResponse(url="/books", status_code=303)
    
    book = get_book_by_id(db, book_id=book_uuid, user_id=user.id)
    if book is None:
        return RedirectResponse(url="/books", status_code=303)
    
    books = get_user_books(db, user_id=user.id)
    notes = sorted(book.notes, key=lambda n: n.number)

    edit_note_raw = request.query_params.get("edit_note_id")
    edit_note_id = None
    if edit_note_raw:
        try:
            edit_note_id = UUID(edit_note_raw)
        except ValueError:
            edit_note_id = None
    
    context = {
        "request": request,
        "books": books,
        "selected_book": book,
        "notes": notes,
        "edit_note_id": edit_note_id,
        "error_add_book": None,
        "error_add_note": None,
        "error_edit_note": None,
    }
    return templates.TemplateResponse("books/detail.html", context)


@router.post("/books", response_model=None)
async def create_book(
    request: Request,
    title: str = Form(""),
    author: str = Form(""),
    db: Session = Depends(get_db),
) -> Response:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    
    user = get_current_user_from_cookie(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    
    if not title.strip() or not author.strip():
        books = get_user_books(db, user_id=user.id)
        context = {
            "request": request,
            "books": books,
            "selected_book": None,
            "notes": [],
            "edit_note_id": None,
            "error_add_book": "Tytuł i autor są wymagane.",
        }
        return templates.TemplateResponse("books/index.html", context)

    create_book_service(db, user_id=user.id, title=title.strip(), author=author.strip())
    return RedirectResponse(url="/books", status_code=303)


@router.post("/books/{book_id}/notes", response_model=None)
async def create_note(
    request: Request,
    book_id: str,
    background_tasks: BackgroundTasks,
    content: str = Form(""),
    db: Session = Depends(get_db),
) -> Response:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    
    user = get_current_user_from_cookie(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        return RedirectResponse(url="/books", status_code=303)
    
    book = get_book_by_id(db, book_id=book_uuid, user_id=user.id)
    if book is None:
        return RedirectResponse(url="/books", status_code=303)
    
    if not content.strip():
        books = get_user_books(db, user_id=user.id)
        notes = sorted(book.notes, key=lambda n: n.number)
        context = {
            "request": request,
            "books": books,
            "selected_book": book,
            "notes": notes,
            "edit_note_id": None,
            "error_add_book": None,
            "error_add_note": "Treść notatki nie może być pusta.",
            "error_edit_note": None,
        }
        return templates.TemplateResponse("books/detail.html", context)

    create_note_service(db, book_id=book_uuid, content=content.strip())

    note_count = count_notes_for_book(db, book_id=book_uuid)
    trigger_analysis_if_needed(
        db,
        book_id=book_uuid,
        user_id=user.id,
        note_count=note_count,
        background_tasks=background_tasks,
    )
    return RedirectResponse(url=f"/books/{book_id}", status_code=303)


@router.post("/notes/{note_id}", response_model=None)
async def update_note(
    request: Request,
    note_id: str,
    background_tasks: BackgroundTasks,
    book_id: str = Form(""),
    content: str = Form(""),
    db: Session = Depends(get_db),
) -> Response:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    
    user = get_current_user_from_cookie(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    
    if not book_id:
        return RedirectResponse(url="/books", status_code=303)

    try:
        note_uuid = UUID(note_id)
        book_uuid = UUID(book_id)
    except ValueError:
        return RedirectResponse(url="/books", status_code=303)
    
    note = get_note_by_id(db, note_id=note_uuid, user_id=user.id)
    if note is None:
        return RedirectResponse(url=f"/books/{book_id}", status_code=303)
    
    book = get_book_by_id(db, book_id=book_uuid, user_id=user.id)

    if not content.strip():
        books = get_user_books(db, user_id=user.id)
        notes = sorted(book.notes, key=lambda n: n.number) if book else []
        context = {
            "request": request,
            "books": books,
            "selected_book": book,
            "notes": notes,
            "edit_note_id": note_id,
            "error_add_book": None,
            "error_add_note": None,
            "error_edit_note": "Treść notatki nie może być pusta.",
        }
        return templates.TemplateResponse("books/detail.html", context)

    update_note_service(db, note=note, content=content.strip())

    note_count = count_notes_for_book(db, book_id=book_uuid)
    trigger_analysis_if_needed(
        db,
        book_id=book_uuid,
        user_id=user.id,
        note_count=note_count,
        background_tasks=background_tasks,
    )
    return RedirectResponse(url=f"/books/{book_id}", status_code=303)
