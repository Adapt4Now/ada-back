from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from app.database import Base, db_config
# Import models so that Base.metadata is populated for Alembic
from app import models  # noqa: F401

config = context.config
fileConfig(config.config_file_name)

DATABASE_URL = db_config.connection_url.replace("asyncpg", "psycopg2")

engine = create_engine(DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
