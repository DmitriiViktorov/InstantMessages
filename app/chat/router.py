import os
from typing import Optional
from fastapi import (
    APIRouter,
    Request,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    BackgroundTasks
)
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from templates_config import templates
from database import get_db

from auth.auth import fastapi_users
from auth.models import User
from .manager import manager
from .utils import get_all_chats, get_chat_messages, get_user_by_id
from .models import Message
from .tasks import notification


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
    await manager.connect(websocket, room_id, user_id=current_user_id)

    current_user = await get_user_by_id(user_id=current_user_id, db=db)
    other_user = await get_user_by_id(user_id=other_user_id, db=db)

    try:
        while True:
            data = await websocket.receive_text()

            message = Message(
                sender_id=current_user.id,
                receiver_id=other_user.id,
                message=data,
            )

            db.add(message)
            await db.commit()

            formatted_message = f"User {current_user.id}: {message.message}"
            await manager.broadcast_to_room(formatted_message, room_id)

            if not manager.is_user_online(other_user_id):
                # await manager.broadcast_to_room("User is offline", room_id)
                notification.delay(
                    current_user_full_name=current_user.full_name,
                    other_user_telegram_id=other_user.telegram_id,
                )


    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, current_user_id)


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

    other_user = await get_user_by_id(user_id=other_user_id, db=db)

    if not other_user or user.id != current_user_id:
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

@router.post("/{current_user_id}/{other_user_id}/download-history")
async def download_chat_history(
        current_user_id: int,
        other_user_id: int,
        background_tasks: BackgroundTasks,
        db: AsyncSession = DEFAULT_DB,
):
    file_path = f"chat_history_{current_user_id}_{other_user_id}.txt"
    current_chat_messages = await get_chat_messages(
        current_user_id=current_user_id,
        other_user_id=other_user_id,
        db=db,
    )
    with open(file_path, "w") as f:
        for message in current_chat_messages:
            f.write(f"From: {message.sender.telegram_account}\n")
            f.write(f"To: {message.receiver.telegram_account}\n")
            f.write(f"Time: {message.created_at}\n")
            f.write(f"{message.message}\n")
            f.write("\n")
    background_tasks.add_task(lambda: os.remove(file_path))
    return FileResponse(
        file_path,
        filename=f"chat_history_{message.sender.telegram_account}_{message.receiver.telegram_account}.txt"
    )

