from fastapi import APIRouter

from app.web.books import router as books_router

router = APIRouter()

router.include_router(books_router)
