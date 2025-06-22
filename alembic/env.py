from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from app.database import Base
from app.database import DATABASE_URL

config = context.config
fileConfig(config.config_file_name)

DATABASE_URL = DATABASE_URL.replace("asyncpg", "psycopg2")

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
