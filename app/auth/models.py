from typing import AsyncGenerator, Optional
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String

from database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    telegram_account: Mapped[str] = mapped_column(String(100), unique=True)
    telegram_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

