"""One model location for training, CLI prediction, and API inference."""
import os
from pathlib import Path
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def resolve_model_path(path=None):
    configured = path or os.getenv("MODEL_PATH") or dotenv_values(PROJECT_ROOT / ".env").get("MODEL_PATH")
    model_path = Path(configured or "ml/model_registry/model.json")
    return model_path if model_path.is_absolute() else PROJECT_ROOT / model_path
