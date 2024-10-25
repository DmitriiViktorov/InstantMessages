from typing import Optional
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from templates_config import templates
from database import get_db

from auth.auth import fastapi_users
from auth.models import User
from .manager import manager
from .utils import get_all_chats, get_chat_messages, get_other_user
from .models import Message


DEFAULT_DB = Depends(get_db)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)



@router.websocket("/ws/{current_user_id}/{other_user_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        current_user_id: int,
        other_user_id: int,
        db: AsyncSession = DEFAULT_DB,
):
    room_id = manager.get_chat_room_id(current_user_id, other_user_id)
    await manager.connect(websocket, room_id)

    try:
        while True:
            data = await websocket.receive_text()

            message = Message(
                sender_id=current_user_id,
                receiver_id=other_user_id,
                message=data,
            )

            db.add(message)
            await db.commit()
            formatted_message = f"User {current_user_id}: {message.message}"
            await manager.broadcast_to_room(formatted_message, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

@router.get("")
async def all_chat_rooms(
        request: Request,
        db: AsyncSession = DEFAULT_DB,
        user: Optional[User] = Depends(fastapi_users.current_user(optional=True))
):
    chats = await get_all_chats(
        current_user_id=user.id,
        db=db
    )
    return templates.TemplateResponse(
        request=request,
        name="chats.html",
        context={
            "current_user_id": user.id,
            "chats": chats,
            "user": user,
        }
    )


@router.get("/{current_user_id}/{other_user_id}")
async def get_chat(
        request: Request,
        current_user_id: int,
        other_user_id: int,
        db: AsyncSession = DEFAULT_DB,
        user: Optional[User] = Depends(fastapi_users.current_user(optional=True))
):
    if not user:
        return RedirectResponse(
            url=request.url_for("login_page"),
        )

    if  user.id != current_user_id:
        return RedirectResponse(
            url=request.url_for("all_chat_rooms"),
        )

    other_user = await get_other_user(other_user_id=other_user_id, db=db)

    if not other_user:
        return RedirectResponse(
            url=request.url_for("all_chat_rooms"),
        )

    chats = await get_all_chats(
        current_user_id=current_user_id,
        db=db
    )
    current_chat_messages = await get_chat_messages(
        current_user_id=current_user_id,
        other_user_id=other_user_id,
        db=db,
    )


    return templates.TemplateResponse(
        request=request,
        name="chat-room.html",
        context={
            "current_user_id": current_user_id,
            "other_user_id": other_user_id,
            "messages": current_chat_messages,
            "user": user,
            "other_user": other_user,
            "chats": chats,
        }
    )

