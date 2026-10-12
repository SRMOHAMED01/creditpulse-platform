"""Tests for the Palier C event-driven (Kafka) async credit flow."""
from uuid import uuid4

import pytest
from app.main import app
from app.routers import credit
from fastapi.testclient import TestClient

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

PREDICTION = {
    "score": 75,
    "probability_default": 0.25,
    "decision": "accepté",
    "explanation": [{"feature": "dti_ratio", "impact": -0.15, "direction": "decreases_risk"}],
    "model_version": "abc" * 64,
}


def register():
    credentials = {"email": f"async-{uuid4().hex}@example.com", "password": "strongpass123"}
    response = client.post("/auth/register", json=credentials)
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


class FakeProducer:
    """Records calls instead of contacting a real Kafka broker."""

    def __init__(self):
        self.calls: list[dict] = []

    def __call__(self, application_id: int, user_id: int, profile: dict):
        self.calls.append({
            "application_id": application_id,
            "user_id": user_id,
            "profile": profile,
        })


@pytest.fixture
def fake_kafka(monkeypatch):
    """Patch publish_credit_request on the module where the router imports it."""
    fake = FakeProducer()
    monkeypatch.setattr("app.kafka.producer.publish_credit_request", fake)
    return fake


def test_apply_async_requires_auth():
    assert client.post("/credit/apply-async", json=APPLICATION).status_code == 401


def test_apply_async_creates_pending_record(fake_kafka):
    headers = register()
    response = client.post("/credit/apply-async", json=APPLICATION, headers=headers)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "pending"
    assert data["requested_amount"] == 10000
    assert data["input_snapshot"] == APPLICATION
    assert len(fake_kafka.calls) == 1
    assert fake_kafka.calls[0]["profile"]["revenu_mensuel"] == 15000


def test_status_endpoint_returns_completed():
    headers = register()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(credit, "predict_credit", lambda profile: dict(PREDICTION))
        create = client.post("/credit/apply", json=APPLICATION, headers=headers)
    app_id = create.json()["id"]

    response = client.get(f"/credit/status/{app_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["score"] == PREDICTION["score"]


def test_status_requires_auth():
    assert client.get("/credit/status/1").status_code == 401


def test_stats_endpoint():
    headers = register()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(credit, "predict_credit", lambda profile: dict(PREDICTION))
        client.post("/credit/apply", json=APPLICATION, headers=headers)

    response = client.get("/credit/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert "avg_score" in data
    assert "accepted" in data
