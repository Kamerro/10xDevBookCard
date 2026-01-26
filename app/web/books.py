from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/books", response_class=HTMLResponse)
async def books_index(request: Request) -> HTMLResponse:
    context = {
        "request": request,
        "books": [],
        "selected_book": None,
        "notes": [],
        "edit_note_id": None,
    }
    return templates.TemplateResponse("books/index.html", context)


@router.get("/books/{book_id}", response_class=HTMLResponse)
async def books_detail(request: Request, book_id: str) -> HTMLResponse:
    context = {
        "request": request,
        "books": [],
        "selected_book": {"id": book_id, "title": "", "author": ""},
        "notes": [],
        "edit_note_id": request.query_params.get("edit_note_id"),
        "error_add_note": None,
        "error_edit_note": None,
    }
    return templates.TemplateResponse("books/detail.html", context)


@router.post("/books/{book_id}/notes")
async def create_note(
    request: Request,
    book_id: str,
    content: str = Form(""),
) -> RedirectResponse | HTMLResponse:
    if not content.strip():
        context = {
            "request": request,
            "books": [],
            "selected_book": {"id": book_id, "title": "", "author": ""},
            "notes": [],
            "edit_note_id": None,
            "error_add_note": "Treść notatki nie może być pusta.",
            "error_edit_note": None,
        }
        return templates.TemplateResponse("books/detail.html", context)

    return RedirectResponse(url=f"/books/{book_id}", status_code=303)


@router.post("/notes/{note_id}")
async def update_note(
    request: Request,
    note_id: str,
    book_id: str = Form(""),
    content: str = Form(""),
) -> RedirectResponse | HTMLResponse:
    if not book_id:
        return RedirectResponse(url="/books", status_code=303)

    if not content.strip():
        context = {
            "request": request,
            "books": [],
            "selected_book": {"id": book_id, "title": "", "author": ""},
            "notes": [],
            "edit_note_id": note_id,
            "error_add_note": None,
            "error_edit_note": "Treść notatki nie może być pusta.",
        }
        return templates.TemplateResponse("books/detail.html", context)

    return RedirectResponse(url=f"/books/{book_id}", status_code=303)
