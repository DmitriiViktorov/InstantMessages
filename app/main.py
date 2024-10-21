from typing import List
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

from sqlalchemy.testing.suite.test_reflection import metadata
from starlette.staticfiles import StaticFiles

from database import engine, Base, SessionLocal
from fastapi.templating import Jinja2Templates
from chat.router import router as router_chat
from auth.router import fastapi_users
from auth.auth import auth_backend
from auth.schemas import UserRead, UserCreate, UserUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    yield
    await SessionLocal().close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "id": 1,
        }
    )


app.include_router(router_chat)
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
