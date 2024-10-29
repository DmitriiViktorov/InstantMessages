from typing import Dict, Set, List
from fastapi import WebSocket



class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.active_users: Set[int] = set()

    def get_chat_room_id(self, user_1_id: int, user_2_id: int) -> str:
        return f"chat_{min(user_1_id, user_2_id)}_{max(user_1_id, user_2_id)}"

    async def connect(self, websocket: WebSocket, room_id: str, user_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        self.active_users.add(user_id)

    def disconnect(self, websocket: WebSocket, room_id: str, user_id: int):
        self.active_connections[room_id].remove(websocket)
        if not self.active_connections[room_id]:
            del self.active_connections[room_id]
        if not any(websocket in connections for connections in self.active_connections.values()):
            self.active_users.discard(user_id)

    async def broadcast_to_room(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.active_users


manager = ConnectionManager()