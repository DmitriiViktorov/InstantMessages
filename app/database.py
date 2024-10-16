from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base


DB_HOST = 'db'
DB_PORT = '5432'
DB_NAME = 'instant_message_db'
DB_USER = 'dmitrii'
DB_PASSWORD = 'strong-admin-password'
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DB_URL, echo=True)
SessionLocal = async_sessionmaker(
    engine, expire_on_commit=False,
    class_=AsyncSession,
    autoflush=True,
)
Base = declarative_base()
