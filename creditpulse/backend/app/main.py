"""
Point d'entrée de l'API FastAPI CreditPulse.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .core.config import settings
from .database import engine
from .logging import setup_logging
from .models import *  # noqa: F401,F403
from .routers import auth, credit, feature_store, users
from .services.ml_service import ScoringUnavailable, check_model_ready

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)
app.add_middleware(
    CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
    allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"],
)

# ============================================================
# PROMETHEUS INSTRUMENTATION (Palier E)
# ============================================================

try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app)
    logger.info("Prometheus metrics enabled at /metrics")
except ImportError:
    logger.warning("prometheus-fastapi-instrumentator not installed; /metrics disabled")


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(credit.router)
app.include_router(feature_store.router)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "CreditPulse API is running",
    }


# ============================================================
# READINESS AND ROOT
# ============================================================

@app.get("/ready")
def readiness_check():
    checks = {"database": "ready", "model": "ready"}
    try:
        with engine.connect() as connection:
            for table in ("users", "financial_profiles", "credit_applications"):
                connection.execute(text(f"SELECT 1 FROM {table} LIMIT 0"))
            connection.execute(text(
                "SELECT input_snapshot, explanation, model_version FROM credit_applications LIMIT 0"
            ))
    except SQLAlchemyError:
        logging.getLogger(__name__).exception("Database readiness failed")
        checks["database"] = "unavailable"
    try:
        check_model_ready()
    except ScoringUnavailable:
        checks["model"] = "unavailable"
    ready = all(value == "ready" for value in checks.values())
    return JSONResponse(
        status_code=200 if ready else 503,
        content={"status": "ready" if ready else "not_ready", "checks": checks},
    )


@app.get("/")
def root():
    return {
        "message": "Welcome to CreditPulse API",
        "docs": "/docs",
    }
