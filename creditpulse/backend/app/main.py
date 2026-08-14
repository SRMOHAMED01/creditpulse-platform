"""
main.py — Point d'entrée de l'API FastAPI
"""

from fastapi import FastAPI
from .core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "CreditPulse API is running"}


@app.get("/")
def root():
    return {
        "message": "Welcome to CreditPulse API",
        "docs": "/docs",
    }
