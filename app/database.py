from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DB_URL, echo=True)
SessionLocal = async_sessionmaker(
    engine, expire_on_commit=False,
    class_=AsyncSession,
    autoflush=True,
)
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get Session with the current database."""
    async with SessionLocal() as db:
        yield db

