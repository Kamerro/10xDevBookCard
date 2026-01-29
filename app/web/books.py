from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


def _require_auth(request: Request) -> Response | None:
    if not request.cookies.get("access_token"):
        return RedirectResponse(url="/login", status_code=303)
    return None


@router.get("/books", response_class=HTMLResponse)
async def books_index(request: Request) -> HTMLResponse:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    context = {
        "request": request,
        "books": [],
        "selected_book": None,
        "notes": [],
        "edit_note_id": None,
        "error_add_book": None,
    }
    return templates.TemplateResponse("books/index.html", context)


@router.get("/books/{book_id}", response_class=HTMLResponse)
async def books_detail(request: Request, book_id: str) -> HTMLResponse:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    context = {
        "request": request,
        "books": [],
        "selected_book": {"id": book_id, "title": "", "author": ""},
        "notes": [],
        "edit_note_id": request.query_params.get("edit_note_id"),
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
) -> Response:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    if not title.strip() or not author.strip():
        context = {
            "request": request,
            "books": [],
            "selected_book": None,
            "notes": [],
            "edit_note_id": None,
            "error_add_book": "Tytuł i autor są wymagane.",
        }
        return templates.TemplateResponse("books/index.html", context)

    return RedirectResponse(url="/books", status_code=303)


@router.post("/books/{book_id}/notes")
@router.post("/books/{book_id}/notes", response_model=None)
async def create_note(
    request: Request,
    book_id: str,
    content: str = Form(""),
) -> Response:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    if not content.strip():
        context = {
            "request": request,
            "books": [],
            "selected_book": {"id": book_id, "title": "", "author": ""},
            "notes": [],
            "edit_note_id": None,
            "error_add_book": None,
            "error_add_note": "Treść notatki nie może być pusta.",
            "error_edit_note": None,
        }
        return templates.TemplateResponse("books/detail.html", context)

    return RedirectResponse(url=f"/books/{book_id}", status_code=303)


@router.post("/notes/{note_id}", response_model=None)
async def update_note(
    request: Request,
    note_id: str,
    book_id: str = Form(""),
    content: str = Form(""),
) -> Response:
    auth_resp = _require_auth(request)
    if auth_resp is not None:
        return auth_resp
    if not book_id:
        return RedirectResponse(url="/books", status_code=303)

    if not content.strip():
        context = {
            "request": request,
            "books": [],
            "selected_book": {"id": book_id, "title": "", "author": ""},
            "notes": [],
            "edit_note_id": note_id,
            "error_add_book": None,
            "error_add_note": None,
            "error_edit_note": "Treść notatki nie może być pusta.",
        }
        return templates.TemplateResponse("books/detail.html", context)

    return RedirectResponse(url=f"/books/{book_id}", status_code=303)
