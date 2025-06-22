import os
from typing import AsyncGenerator
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Environment variable names
ENV_DB_USER = "DB_USER"
ENV_DB_PASSWORD = "DB_PASSWORD"
ENV_DB_HOST = "DB_HOST"
ENV_DB_PORT = "DB_PORT"
ENV_DB_NAME = "DB_NAME"

# Database default settings
DEFAULT_DB_CREDENTIALS = {
    "user": "postgres",
    "password": "password",
    "host": "postgres_db",
    #"host": "localhost",
    "port": "5432",
    "name": "tasks_db"
}

# Connection pool settings
@dataclass
class PoolConfig:
    """Configuration for the database connection pool."""
    size: int = field(default=5)
    max_overflow: int = field(default=10)
    timeout: int = field(default=30)

    def __post_init__(self):
        """Validate pool configuration values."""
        if self.size <= 0:
            raise ValueError("Pool size must be positive")
        if self.max_overflow < 0:
            raise ValueError("Max overflow must be non-negative")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

class DatabaseConnectionError(SQLAlchemyError):
    """Raised when a database connection fails."""
    pass

@dataclass
class DatabaseConfig:
    """Configuration for database connection."""
    user: str = os.getenv(ENV_DB_USER, DEFAULT_DB_CREDENTIALS["user"])
    password: str = os.getenv(ENV_DB_PASSWORD, DEFAULT_DB_CREDENTIALS["password"])
    host: str = os.getenv(ENV_DB_HOST, DEFAULT_DB_CREDENTIALS["host"])
    port: str = os.getenv(ENV_DB_PORT, DEFAULT_DB_CREDENTIALS["port"])
    name: str = os.getenv(ENV_DB_NAME, DEFAULT_DB_CREDENTIALS["name"])
    pool: PoolConfig = PoolConfig()

    @property
    def connection_url(self) -> str:
        """Generates database connection URL."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class DatabaseSessionManager:
    """Manages database engine and sessions."""
    
    SESSION_AUTOCOMMIT = False
    SESSION_AUTOFLUSH = False
    
    def __init__(self, config: DatabaseConfig):
        self._engine: AsyncEngine = create_async_engine(
            config.connection_url,
            echo=False,
            pool_size=config.pool.size,
            max_overflow=config.pool.max_overflow,
            pool_timeout=config.pool.timeout
        )
        self._session_factory = self._configure_session_factory()

    def _configure_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Configures and returns an async session factory.

        Returns:
            async_sessionmaker[AsyncSession]: Configured async session factory.
        """
        return async_sessionmaker(
            self._engine,
            autocommit=self.SESSION_AUTOCOMMIT,
            autoflush=self.SESSION_AUTOFLUSH,
            class_=AsyncSession,
            expire_on_commit=False
        )


    async def close(self) -> None:
        """Close the database engine and release all resources."""
        if self._engine is not None:
            await self._engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Creates and yields database session.
        Yields:
            AsyncSession: Database session that will be automatically closed after usage.
        Raises:
            DatabaseConnectionError: If database connection fails
        """
        try:
            async with self._session_factory() as session:
                yield session
        except SQLAlchemyError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}") from e

Base = declarative_base()
db_config = DatabaseConfig()
db_manager = DatabaseSessionManager(db_config)
get_database_session = db_manager.get_session