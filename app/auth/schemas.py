from typing import Optional
from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    first_name: str
    last_name: str
    nick_name: str

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    nick_name: str

    class Config:
        from_attributes = True


class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nick_name: Optional[str] = None