from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.auth_service import authenticate_user, create_access_token

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    context = {"request": request, "title": "Logowanie"}
    return templates.TemplateResponse("auth/login.html", context)


@router.post("/login", response_model=None)
async def login_submit(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    db: Session = Depends(get_db),
) -> Response:
    user = authenticate_user(db, email=email, password=password)
    if user is None:
        context = {"request": request, "title": "Logowanie", "error_login": "Nieprawidłowy email lub hasło."}
        return templates.TemplateResponse("auth/login.html", context)

    token = create_access_token(user_id=str(user.id))

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request) -> HTMLResponse:
    context = {"request": request, "title": "Rejestracja"}
    return templates.TemplateResponse("auth/register.html", context)


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request) -> HTMLResponse:
    context = {"request": request, "title": "Odzyskiwanie hasła"}
    return templates.TemplateResponse("auth/forgot_password.html", context)
