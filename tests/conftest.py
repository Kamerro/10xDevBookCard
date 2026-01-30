from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.main import create_app
from app.models.base import Base
import app.models  # noqa: F401
from app.services.auth_service import create_access_token, create_user


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def db_session(engine) -> Session:
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    app = create_app()

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


@pytest.fixture()
def user_a(db_session: Session):
    return create_user(db_session, email="a@example.com", password="Password1!")


@pytest.fixture()
def user_b(db_session: Session):
    return create_user(db_session, email="b@example.com", password="Password1!")


@pytest.fixture()
def token_a(user_a) -> str:
    return create_access_token(user_id=str(user_a.id))


@pytest.fixture()
def token_b(user_b) -> str:
    return create_access_token(user_id=str(user_b.id))


@pytest.fixture()
def auth_header_a(token_a: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_a}"}


@pytest.fixture()
def auth_header_b(token_b: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_b}"}
