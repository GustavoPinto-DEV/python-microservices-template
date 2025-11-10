"""
Conexión asíncrona a PostgreSQL
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from repositorio_lib.config.settings import db_settings

# URL de conexión
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{db_settings.DB_USER}:{db_settings.DB_PASSWORD}"
    f"@{db_settings.DB_HOST}:{db_settings.DB_PORT}/{db_settings.DB_NAME}"
)

# Engine asíncrono con pool de conexiones
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
)

# SessionLocal para crear sesiones
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager para obtener sesión asíncrona.

    Uso:
        async with get_async_session() as db:
            # Operaciones con db
            await db.commit()
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
