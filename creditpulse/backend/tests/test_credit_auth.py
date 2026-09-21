from datetime import timedelta

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app
from app.routers import credit


client = TestClient(app)
APPLICATION = {
    "revenu_mensuel": 15000,
    "dettes_actuelles": 3000,
    "age": 30,
    "anciennete_emploi": 5,
    "nombre_credits_en_cours": 1,
    "historique_paiement": 0.95,
    "requested_amount": 10000,
    "duration_months": 12,
}


def test_credit_application_requires_authentication():
    response = client.post("/credit/apply", json=APPLICATION)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_authenticated_user_can_reach_scoring(monkeypatch):
    register_response = client.post(
        "/auth/register",
        json={"email": "credit-user@example.com", "password": "strongpass123"},
    )
    token = register_response.json()["access_token"]
    monkeypatch.setattr(
        credit,
        "predict_credit",
        lambda profile: {
            "score": 70,
            "probability_default": 0.3,
            "decision": "accepté",
            "explanation": [],
        },
    )

    response = client.post(
        "/credit/apply",
        json=APPLICATION,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["score"] == 70


def test_token_with_invalid_subject_is_rejected():
    token = create_access_token({"sub": "not-a-user-id"})

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_expired_token_is_rejected():
    token = create_access_token(
        {"sub": "1"},
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
