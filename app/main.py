import asyncio
from typing import Optional
from fastapi import FastAPI, Request, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from alembic import command
from alembic.config import Config

from templates_config import templates
from database import engine, SessionLocal
from chat.router import router as router_chat
from auth.router import router as auth_router
from auth.auth import auth_backend, fastapi_users
from auth.schemas import UserRead, UserCreate, UserUpdate
from auth.models import User


async def run_async_migrations():
    def sync_upgrade():
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

    await asyncio.to_thread(sync_upgrade)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_async_migrations()

    redis = aioredis.from_url("redis://cache:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await SessionLocal().close()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", name="home")
async def root(
        request: Request,
        user: Optional[User] = Depends(fastapi_users.current_user(optional=True))
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "id": 1,
            "user": user,
        }
    )


app.include_router(router_chat)
app.include_router(auth_router)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
