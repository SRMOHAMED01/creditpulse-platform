"""
database.py — Configuration de la base de données
"""

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from .core.config import PROJECT_ROOT, settings

logger = logging.getLogger(__name__)


def build_engine(url: str | None = None):
    """Create the SQLAlchemy engine for the configured DATABASE_URL.

    If the configured URL is unreachable (e.g. PostgreSQL not running in
    local development), fall back to SQLite so callers stay functional.
    """
    url = url or settings.DATABASE_URL

    try:
        engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5} if url.startswith("postgresql") else {},
        )
        # Probe the connection once at startup to decide on fallback.
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return engine
    except (SQLAlchemyError, OSError) as exc:
        logger.warning(
            "Database at %s is unreachable (%s); falling back to SQLite.",
            url,
            exc,
        )
        fallback_path = PROJECT_ROOT / "creditpulse_runtime.db"
        return create_engine(
            f"sqlite:///{fallback_path}",
            connect_args={"check_same_thread": False},
        )


engine = build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
