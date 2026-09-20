"""
database.py — Configuration de la base de données
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .core.config import settings

engine = create_engine(
    settings.DATABASE_URL, pool_pre_ping=True,
    connect_args={"connect_timeout": 5} if settings.DATABASE_URL.startswith("postgresql") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
