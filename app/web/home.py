from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request) -> HTMLResponse:
    context = {"request": request, "title": "BookCards"}
    return templates.TemplateResponse("home.html", context)
