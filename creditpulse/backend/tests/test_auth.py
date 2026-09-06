from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_and_login_flow():
    register_response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "strongpass123",
        },
    )

    assert register_response.status_code == 201
    payload = register_response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"

    login_response = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "strongpass123",
        },
    )

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
