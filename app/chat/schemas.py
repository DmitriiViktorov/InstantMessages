from pydantic import BaseModel
from typing import Optional, List
from auth.schemas import UserRead


class ChatContext(BaseModel):
    current_user_id: int
    chats: List[dict]
    user: Optional[UserRead] = None