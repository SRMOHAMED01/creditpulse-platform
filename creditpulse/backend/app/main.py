"""
Point d'entrée de l'API FastAPI CreditPulse.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging

from .core.config import settings
from .models import *  # noqa: F401,F403
from .routers import auth, credit, users
from .database import engine
from .services.ml_service import check_model_ready, ScoringUnavailable

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)
app.add_middleware(
    CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
    allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(credit.router)


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
