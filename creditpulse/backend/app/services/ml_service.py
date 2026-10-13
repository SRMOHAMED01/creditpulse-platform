"""Boundary between the API and the optional native ML runtime."""

import logging
import sys
from pathlib import Path

from ..core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
logger = logging.getLogger(__name__)


class ScoringUnavailable(RuntimeError):
    """Model, dependencies, or explanation engine cannot serve requests."""


def get_feature_store_values(db_session, user_id: int) -> dict | None:
    """Look up dbt-computed features from the feature_store table (Palier B).

    Returns a dict with ``dti_ratio`` and ``score_regularite`` if the
    user's feature-store row exists, otherwise ``None``.
    """
    try:
        from ..models.feature_store import FeatureStore

        record = db_session.query(FeatureStore).filter(
            FeatureStore.user_id == user_id
        ).first()
        if record is None:
            return None
        return {
            "dti_ratio": record.dti_ratio,
            "score_regularite": record.score_regularite,
        }
    except Exception:
        logger.exception("Feature store lookup failed for user_id=%s", user_id)
        return None


def predict_credit(profile: dict) -> dict:
    try:
        from ml.serve import predict

        result = predict(profile, model_path=str(settings.MODEL_PATH))

        # Palier D: log predictions to MLflow for monitoring
        try:
            import os

            import mlflow

            mlflow.set_tracking_uri(
                os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
            )
            mlflow.set_experiment("creditpulse-credit-scoring")
            with mlflow.start_run(run_name="inference"):
                mlflow.log_metric("score", result["score"])
                mlflow.log_metric("probability_default", result["probability_default"])
                mlflow.log_metric(
                    "decision_accepted", 1 if result["decision"] == "accepté" else 0
                )
        except Exception:
            logger.warning("MLflow logging skipped (not configured)")

        return result
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        logger.exception("Scoring unavailable; check dependencies and MODEL_PATH")
        raise ScoringUnavailable(
            "Scoring is unavailable. Check the server model and dependency configuration."
        ) from exc


def check_model_ready() -> None:
    try:
        from ml.serve import get_model

        get_model(str(settings.MODEL_PATH))
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        raise ScoringUnavailable("The configured scoring model is not ready.") from exc
