from fastapi import FastAPI

from app.api.router import api_router
from app.web.router import router as web_router


def create_app() -> FastAPI:
    app = FastAPI(title="BookCards")

    app.include_router(api_router)
    app.include_router(web_router)

    return app


app = create_app()
