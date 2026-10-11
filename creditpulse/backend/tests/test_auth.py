from app.main import app
from fastapi.testclient import TestClient

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
