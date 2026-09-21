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

def predict_credit(profile: dict) -> dict:
    try:
        from ml.serve import predict
        return predict(profile, model_path=str(settings.MODEL_PATH))
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
