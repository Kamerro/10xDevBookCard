from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.api.router import api_router
from app.web.router import router as web_router


def create_app() -> FastAPI:
    app = FastAPI(title="BookCards")

    # Use absolute path for static files in Docker
    static_dir = os.path.join(os.getcwd(), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    app.include_router(api_router, prefix="/api")
    app.include_router(web_router)

    return app


app = create_app()
