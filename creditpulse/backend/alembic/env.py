from logging.config import fileConfig

from alembic import context
from app.core.config import settings
from app.database import Base, build_engine
from app.models import CreditApplication, FinancialProfile, User  # noqa: F401
from sqlalchemy import pool

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit migrations as SQL without connecting to a database."""
    context.configure(
        url=str(settings.DATABASE_URL),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the configured database, resolving the
    SQLite fallback the same way the application does."""
    connectable = build_engine(str(settings.DATABASE_URL))

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                poolclass=pool.NullPool,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
