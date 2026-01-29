from fastapi import APIRouter

from app.web.auth import router as auth_router
from app.web.books import router as books_router
from app.web.home import router as home_router

router = APIRouter()

router.include_router(home_router)
router.include_router(auth_router)
router.include_router(books_router)
