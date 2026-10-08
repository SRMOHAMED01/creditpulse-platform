"""Exercise real API/database persistence, with only native inference replaced."""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import credit
from app.services.ml_service import ScoringUnavailable

client = TestClient(app)
APPLICATION = {
    "revenu_mensuel": 15000, "dettes_actuelles": 3000, "age": 30,
    "anciennete_emploi": 5, "nombre_credits_en_cours": 1,
    "historique_paiement": 0.95, "requested_amount": 10000, "duration_months": 12,
}
PREDICTION = {
    "score": 70, "probability_default": 0.3, "decision": "accepté",
    "explanation": [{"feature": "dti_ratio", "impact": -0.2, "direction": "decreases_risk"}],
    "model_version": "a" * 64,
}


def register():
    credentials = {"email": f"{uuid4().hex}@example.com", "password": "strongpass123"}
    response = client.post("/auth/register", json=credentials)
    assert response.status_code == 201
    return credentials, {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def scoring(monkeypatch):
    monkeypatch.setattr(credit, "predict_credit", lambda profile: dict(PREDICTION))


def test_assessment_survives_new_login_and_preserves_inputs(scoring):
    credentials, headers = register()
    response = client.post("/credit/apply", json=APPLICATION, headers=headers)
    assert response.status_code == 200
    saved = response.json()
    assert saved["input_snapshot"] == APPLICATION
    assert saved["explanation"] == PREDICTION["explanation"]
    assert saved["model_version"] == PREDICTION["model_version"]
    assert saved["created_at"].endswith("Z")
    login = client.post("/auth/login", json=credentials)
    new_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get(f"/credit/applications/{saved['id']}", headers=new_headers).json() == saved
    assert client.get("/credit/applications", headers=new_headers).json() == [saved]


def test_history_is_private_and_missing_ids_return_404(scoring):
    _, owner = register()
    _, other = register()
    saved = client.post("/credit/apply", json=APPLICATION, headers=owner).json()
    assert client.get("/credit/applications", headers=other).json() == []
    assert client.get(f"/credit/applications/{saved['id']}", headers=other).status_code == 404
    assert client.get("/credit/applications/2147483647", headers=owner).status_code == 404


@pytest.mark.parametrize("path", ["/credit/applications", "/credit/applications/1"])
def test_history_requires_authentication(path):
    assert client.get(path).status_code == 401


def test_history_order_and_pagination(scoring):
    _, headers = register()
    first = client.post("/credit/apply", json=APPLICATION, headers=headers).json()
    second = client.post("/credit/apply", json={**APPLICATION, "requested_amount": 20000}, headers=headers).json()
    assert client.get("/credit/applications?limit=1", headers=headers).json() == [second]
    assert client.get("/credit/applications?limit=1&offset=1", headers=headers).json() == [first]
    assert client.get("/credit/applications?offset=2", headers=headers).json() == []
    for query in ("limit=0", "limit=101", "offset=-1"):
        assert client.get(f"/credit/applications?{query}", headers=headers).status_code == 422


def test_failed_scoring_does_not_create_history(monkeypatch):
    _, headers = register()

    def unavailable(profile):
        raise ScoringUnavailable("Scoring unavailable")

    monkeypatch.setattr(credit, "predict_credit", unavailable)
    assert client.post("/credit/apply", json=APPLICATION, headers=headers).status_code == 503
    assert client.get("/credit/applications", headers=headers).json() == []


def test_invalid_application_does_not_create_history(scoring):
    _, headers = register()
    response = client.post("/credit/apply", json={**APPLICATION, "requested_amount": -1}, headers=headers)
    assert response.status_code == 422
    assert client.get("/credit/applications", headers=headers).json() == []
