import uuid

from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from .models import User
from .manager import get_user_manager
from .auth import auth_backend


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

