from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.auth_service import authenticate_user, create_access_token, create_user

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    context = {"request": request, "title": "Logowanie"}
    return templates.TemplateResponse("auth/auth_combined.html", context)


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
        return templates.TemplateResponse("auth/auth_combined.html", context)

    token = create_access_token(user_id=str(user.id))

    response = RedirectResponse(url="/books", status_code=303)
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
    return templates.TemplateResponse("auth/auth_combined.html", context)


@router.post("/register", response_model=None)
async def register_submit(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    password_confirm: str = Form(""),
    db: Session = Depends(get_db),
) -> Response:
    if password != password_confirm:
        context = {
            "request": request,
            "title": "Rejestracja",
            "error_register": "Hasła nie są takie same.",
        }
        return templates.TemplateResponse("auth/auth_combined.html", context)

    try:
        user = create_user(db, email=email, password=password)
    except ValueError as e:
        msg = "Niepoprawne dane rejestracji."
        if str(e) == "email_taken":
            msg = "Email jest już zajęty."
        elif str(e) == "password_invalid_length":
            msg = "Hasło musi mieć 8–19 znaków."
        elif str(e) == "password_missing_uppercase":
            msg = "Hasło musi zawierać co najmniej 1 wielką literę."
        elif str(e) == "password_missing_digit":
            msg = "Hasło musi zawierać co najmniej 1 cyfrę."
        elif str(e) == "password_missing_special":
            msg = "Hasło musi zawierać co najmniej 1 znak specjalny."

        context = {"request": request, "title": "Rejestracja", "error_register": msg}
        return templates.TemplateResponse("auth/auth_combined.html", context)

    token = create_access_token(user_id=str(user.id))
    response = RedirectResponse(url="/books", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/logout", response_model=None)
async def logout_submit() -> Response:
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request) -> HTMLResponse:
    context = {"request": request, "title": "Odzyskiwanie hasła"}
    return templates.TemplateResponse("auth/forgot_password.html", context)
