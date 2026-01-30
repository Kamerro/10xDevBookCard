from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.web.router import router as web_router


def create_app() -> FastAPI:
    app = FastAPI(title="BookCards")

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(api_router, prefix="/api")
    app.include_router(web_router)

    return app


app = create_app()
