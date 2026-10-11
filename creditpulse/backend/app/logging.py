"""
logging.py — Structured logging configuration.
"""

import logging
import sys


def setup_logging(level: str | None = None) -> None:
    """Configure structured JSON-ish logging for the API."""
    log_level = (level or "INFO").upper()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    # Quiet noisy libraries
    for noisy in ("sqlalchemy.engine", "sqlalchemy.pool", "alembic.runtime"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
