import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Add the project root to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Import your Base and models so Alembic knows about them
from app.database import Base
import app.models  # noqa: F401, ensures all models are registered with Base

# this is the Alembic Config object, which provides access to the .ini file values
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Set target_metadata for 'autogenerate'
target_metadata = Base.metadata

# DB URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set for Alembic")

config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode (generates SQL without connecting)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode (connects to DB)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
