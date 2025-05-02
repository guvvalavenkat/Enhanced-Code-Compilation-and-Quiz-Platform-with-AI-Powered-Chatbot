import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# ---------------------- CONFIGURATION ------------------------

# Your Railway DB URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:KroLYKAvjymiiGjaKiEgKwXwbzLQnvr@metro.proxy.rlwy.net:36971/railway"
)

# Alembic Config object
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Set database URL explicitly
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Import your model's metadata object here for 'autogenerate' support
from models import db
target_metadata = db.metadata

# ---------------------- MIGRATION LOGIC -----------------------

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
