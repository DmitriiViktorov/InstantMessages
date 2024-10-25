from typing import Dict
from fastapi import APIRouter
from typing import List

from fastapi import Request, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select

from sqlalchemy.orm import Session
from templates_config import templates
from .models import Message
from database import get_db



DEFAULT_DB = Depends(get_db)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    def get_chat_room_id(self, user_1_id: int, user_2_id: int) -> str:
        return f"chat_{min(user_1_id, user_2_id)}_{max(user_1_id, user_2_id)}"

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        self.active_connections[room_id].remove(websocket)
        if not self.active_connections[room_id]:
            del self.active_connections[room_id]

    async def broadcast_to_room(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{current_user_id}/{other_user_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        current_user_id: int,
        other_user_id: int,
        db: Session = DEFAULT_DB,
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


@router.get("/{current_user_id}/{other_user_id}")
async def get_chat(
        request: Request,
        current_user_id: int,
        other_user_id: int,
        db: Session = DEFAULT_DB,
):
    async with db:
        messages_query = select(Message).filter(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user_id))
        ).order_by(Message.created_at)
        result = await db.execute(messages_query)
        messages = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="chat-room.html",
        context={
            "current_user_id": current_user_id,
            "other_user_id": other_user_id,
            "messages": messages,
        }

    )