import asyncio
from typing import AsyncGenerator
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger("aquapulse.database")

Base = declarative_base()

# Resilient Engine Setup
HAS_AIOSQLITE = False
try:
    import aiosqlite  # type: ignore
    HAS_AIOSQLITE = True
except ImportError:
    HAS_AIOSQLITE = False

db_url = settings.DATABASE_URL
USE_ASYNC = False

if db_url.startswith("postgresql"):
    USE_ASYNC = True
    if not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
elif HAS_AIOSQLITE and "sqlite" in db_url:
    USE_ASYNC = True
    if not db_url.startswith("sqlite+aiosqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
else:
    USE_ASYNC = False
    if "+aiosqlite" in db_url:
        db_url = db_url.replace("sqlite+aiosqlite://", "sqlite://")

if USE_ASYNC:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
else:
    connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
    sync_engine = create_engine(
        db_url,
        echo=False,
        connect_args=connect_args,
        future=True
    )
    SyncSessionLocal = sessionmaker(
        bind=sync_engine,
        autocommit=False,
        autoflush=False
    )

class DatabaseSessionContext:
    def __init__(self):
        self._session = None

    async def __aenter__(self):
        if USE_ASYNC:
            self._session = AsyncSessionLocal()
            return self._session
        else:
            self._session = SyncSessionLocal()
            return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            if exc_type is not None:
                if USE_ASYNC:
                    await self._session.rollback()
                else:
                    self._session.rollback()
            else:
                if USE_ASYNC:
                    await self._session.commit()
                else:
                    self._session.commit()
            if USE_ASYNC:
                await self._session.close()
            else:
                self._session.close()

    def __enter__(self):
        self._session = SyncSessionLocal()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            if exc_type is not None:
                self._session.rollback()
            else:
                self._session.commit()
            self._session.close()

def get_session():
    return DatabaseSessionContext()

async def get_db():
    async with get_session() as session:
        yield session

def init_db_sync():
    """Synchronous database table creation."""
    import app.db.models  # ensure models are registered
    Base.metadata.create_all(bind=sync_engine)

async def init_db():
    """Create all tables in the database."""
    import app.db.models  # ensure models are registered
    if USE_ASYNC:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        init_db_sync()
    logger.info("Database tables initialized successfully.")
