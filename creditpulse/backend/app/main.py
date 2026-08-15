"""
Point d'entrée de l'API FastAPI CreditPulse.
"""

from fastapi import FastAPI

from .core.config import settings
from .routers import credit


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    credit.router
)


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