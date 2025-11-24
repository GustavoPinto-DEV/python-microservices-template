"""
Database Configuration - Async PostgreSQL with SQLAlchemy

Async PostgreSQL connection configuration using SQLAlchemy 2.0+
with support for async contexts, Alembic migrations and test mode.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from repositorio_lib.config import db_settings


# ----------------------------------------------------------------------
# Base for SQLAlchemy models
# ----------------------------------------------------------------------
Base = declarative_base()


# ----------------------------------------------------------------------
# Dynamic connection string
# ----------------------------------------------------------------------
DATABASE_URL = db_settings.get_connection_string(async_mode=True)


# ----------------------------------------------------------------------
# Async engine (main)
# ----------------------------------------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=db_settings.DB_ECHO,
    pool_size=db_settings.POOL_SIZE,
    max_overflow=db_settings.MAX_OVERFLOW,
    pool_pre_ping=db_settings.POOL_PRE_PING,
    pool_recycle=db_settings.POOL_RECYCLE,
    pool_timeout=db_settings.POOL_TIMEOUT,
)


# ----------------------------------------------------------------------
# Async session maker
# ----------------------------------------------------------------------
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


# ----------------------------------------------------------------------
# Session dependency (for FastAPI)
# ----------------------------------------------------------------------
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ----------------------------------------------------------------------
# Manual context manager (for scripts or services)
# ----------------------------------------------------------------------
@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for use in services or scripts without FastAPI.

    Example:
        async with get_db_context() as db:
            await repository.create(db, data)
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ----------------------------------------------------------------------
# Database initialization / cleanup functions
# ----------------------------------------------------------------------
async def init_db():
    """
    Initializes the database by creating all tables.

    ⚠️ Only use in development or tests.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """
    Drops all tables from the database.

    ⚠️ Dangerous: only use in development or tests.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ----------------------------------------------------------------------
# Sync engine and session (for Alembic or migration scripts)
# ----------------------------------------------------------------------
SYNC_DATABASE_URL = db_settings.get_connection_string(async_mode=False)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=db_settings.DB_ECHO,
    pool_pre_ping=db_settings.POOL_PRE_PING,
)

sync_session_maker = sessionmaker(sync_engine, expire_on_commit=False)


def get_sync_session():
    """
    Synchronous session context (for migrations or scripts).
    """
    session = sync_session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
