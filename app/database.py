from typing import AsyncGenerator
from dataclasses import dataclass, field
from fastapi import Request
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

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
    user: str = settings.current_config.db_user
    password: str = settings.current_config.db_password
    host: str = settings.current_config.db_host
    port: int = settings.current_config.db_port
    name: str = settings.current_config.db_name
    pool: PoolConfig = field(default_factory=PoolConfig)

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

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Expose configured session factory."""
        return self._session_factory


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


class UnitOfWork:
    """Unit of work for managing database transactions."""

    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession], *, auto_commit: bool = True
    ):
        self._session_factory = session_factory
        self.session: AsyncSession | None = None
        self._auto_commit = auto_commit

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None and self.session is not None:
            await self.session.rollback()
        elif self._auto_commit and self.session is not None:
            await self.session.commit()
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def commit(self) -> None:
        if self.session is not None:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session is not None:
            await self.session.rollback()

def create_db_manager(config: DatabaseConfig) -> DatabaseSessionManager:
    """Create a new instance of :class:`DatabaseSessionManager`.

    Args:
        config: Database configuration.

    Returns:
        DatabaseSessionManager: Initialized session manager.
    """

    return DatabaseSessionManager(config)


async def get_database_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session."""

    db_manager: DatabaseSessionManager = request.app.state.db_manager
    async for session in db_manager.get_session():
        yield session
