"""Tests for the feature store sync endpoint (Palier B)."""
import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def register_and_login(client, email="feature@example.com", password="strongpass123"):
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_sync_requires_authentication():
    assert client.post("/feature-store/sync").status_code == 401


def test_sync_requires_existing_profile():
    headers = register_and_login(client, email="nop@example.com")
    response = client.post("/feature-store/sync", headers=headers)
    assert response.status_code == 404


def test_sync_creates_feature_store_row():
    headers = register_and_login(client, email="sync@example.com")
    # Create profile first
    profile_response = client.post(
        "/users/profile",
        headers=headers,
        json={
            "revenu_mensuel": 5000,
            "dettes_actuelles": 1200,
            "age": 32,
            "anciennete_emploi": 6,
            "nombre_credits_en_cours": 2,
            "historique_paiement": 0.8,
        },
    )
    assert profile_response.status_code == 200

    response = client.post("/feature-store/sync", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["dti_ratio"] == pytest.approx(0.24, abs=0.01)
    assert data["score_regularite"] == 0.8


def test_sync_is_idempotent():
    headers = register_and_login(client, email="idem@example.com")
    client.post(
        "/users/profile",
        headers=headers,
        json={
            "revenu_mensuel": 4000,
            "dettes_actuelles": 800,
            "age": 28,
            "anciennete_emploi": 3,
            "nombre_credits_en_cours": 1,
            "historique_paiement": 0.9,
        },
    )
    first = client.post("/feature-store/sync", headers=headers)
    second = client.post("/feature-store/sync", headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["profile_id"] == second.json()["profile_id"]
