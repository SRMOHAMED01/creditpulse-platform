"""Verify upgrades preserve existing assessments and support clean installs."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from app.core.config import settings
from app.models.credit_application import CreditApplication
from app.schemas.credit import SavedCreditApplicationResponse
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session


def test_history_migration_preserves_legacy_results(tmp_path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'migration.db').as_posix()}"
    monkeypatch.setattr(settings, "DATABASE_URL", url)
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "20260921_0001")
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO users (id, email, hashed_password) VALUES (1, 'legacy@example.com', 'hash')"))
        connection.execute(text("""INSERT INTO credit_applications
            (id, user_id, requested_amount, duration_months, score, probability_default, decision, created_at)
            VALUES (1, 1, 10000, 12, 70, 0.3, 'accepted', '2026-09-21 12:00:00')"""))
    command.upgrade(config, "head")
    with Session(engine) as session:
        legacy = session.get(CreditApplication, 1)
        response = SavedCreditApplicationResponse.model_validate(legacy)
        assert response.score == 70
        assert response.input_snapshot is None
        assert response.explanation is None
        assert response.model_version is None
        assert response.created_at.utcoffset().total_seconds() == 0
    assert "ix_credit_applications_user_created" in {item["name"] for item in inspect(engine).get_indexes("credit_applications")}
    command.downgrade(config, "20260921_0001")
    with engine.connect() as connection:
        assert connection.execute(text("SELECT score FROM credit_applications WHERE id=1")).scalar_one() == 70
    command.upgrade(config, "head")
    engine.dispose()
