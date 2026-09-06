"""
Point d'entrée de l'API FastAPI CreditPulse.
"""

from fastapi import FastAPI

from .core.config import settings
from .models import *  # noqa: F401,F403
from .routers import auth, credit, users

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
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
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to CreditPulse API",
        "docs": "/docs",
    }