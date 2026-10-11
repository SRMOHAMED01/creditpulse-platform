"""
database.py — Configuration de la base de données
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .core.config import settings

logger = logging.getLogger(__name__)


def _build_engine():
    """Create the SQLAlchemy engine, falling back to SQLite when the
    configured PostgreSQL driver cannot be loaded (e.g. blocked DLLs)."""
    url = settings.DATABASE_URL
    try:
        return create_engine(
            url, pool_pre_ping=True,
            connect_args={"connect_timeout": 5} if url.startswith("postgresql") else {},
        )
    except (ImportError, OSError) as exc:
        logger.warning(
            "PostgreSQL driver unavailable (%s); falling back to SQLite for this process.",
            exc,
        )
        return create_engine(
            "sqlite:///creditpulse_runtime.db",
            connect_args={"check_same_thread": False},
        )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
