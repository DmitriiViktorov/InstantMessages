from typing import Optional
from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager

from starlette.staticfiles import StaticFiles

from database import engine, Base, SessionLocal
from chat.router import router as router_chat
from auth.router import router as auth_router
from auth.auth import auth_backend, fastapi_users
from auth.schemas import UserRead, UserCreate, UserUpdate
from auth.models import User

from templates_config import templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all, checkfirst=True)
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
