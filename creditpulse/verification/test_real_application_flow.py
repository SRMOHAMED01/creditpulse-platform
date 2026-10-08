"""Exercise migrations, real inference, authentication, and durable API results."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import main
from app.core.config import settings
from app.database import get_db


def test_complete_api_flow_with_genuine_model(tmp_path, monkeypatch):
    database_url = f"sqlite:///{(tmp_path / 'genuine-flow.db').as_posix()}"
    monkeypatch.setattr(settings, "DATABASE_URL", database_url)
    config = Config(str(Path(__file__).resolve().parents[1] / "backend" / "alembic.ini"))
    command.upgrade(config, "head")
    engine = create_engine(database_url, connect_args={"check_same_thread": False})

    def database_session():
        with Session(engine) as session:
            yield session

    monkeypatch.setitem(main.app.dependency_overrides, get_db, database_session)
    monkeypatch.setattr(main, "engine", engine)
    credentials = {"email": "genuine-flow@example.com", "password": "GenuineFlow123!"}
    profile = {
        "revenu_mensuel": 12000, "dettes_actuelles": 1800, "age": 35,
        "anciennete_emploi": 7, "nombre_credits_en_cours": 2, "historique_paiement": 0.95,
    }
    try:
        with TestClient(main.app) as client:
            assert client.get("/ready").status_code == 200
            registered = client.post("/auth/register", json=credentials)
            assert registered.status_code == 201
            headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}
            assert client.post("/users/profile", headers=headers, json=profile).status_code == 200
            assert client.get("/users/profile", headers=headers).json()["revenu_mensuel"] == 12000
            application = {**profile, "requested_amount": 10000, "duration_months": 24}
            response = client.post("/credit/apply", headers=headers, json=application)
            assert response.status_code == 200
            saved = response.json()
            assert saved["input_snapshot"] == application
            assert len(saved["explanation"]) == 7
            assert len(saved["model_version"]) == 64
            assert 0 <= saved["probability_default"] <= 1

        with TestClient(main.app) as returning:
            login = returning.post("/auth/login", json=credentials)
            assert login.status_code == 200
            headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
            assert returning.get("/credit/applications", headers=headers).json() == [saved]
            assert returning.get(f"/credit/applications/{saved['id']}", headers=headers).json() == saved
            other = returning.post("/auth/register", json={**credentials, "email": "other-flow@example.com"})
            other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}
            assert returning.get(f"/credit/applications/{saved['id']}", headers=other_headers).status_code == 404
    finally:
        engine.dispose()
