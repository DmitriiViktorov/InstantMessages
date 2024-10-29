import uuid
from typing import Optional, Any

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidID

from .models import User, get_user_db

from config import PASSWORD_RESET


SECRET = PASSWORD_RESET


class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def parse_id(self, value: Any) -> int:
        try:
            return int(value)
        except ValueError as e:
            raise InvalidID() from e

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

