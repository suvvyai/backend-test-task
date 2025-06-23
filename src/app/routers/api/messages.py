from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.database.models import Channel
from src.core.schemas.message import MessageSend
from src.services.send import send_message_to_channel_logic

security = HTTPBearer()

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/send", status_code=202)
async def send_message_to_channel(
    data: MessageSend,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict[str, str]:
    # 1. Извлечение токена
    token = credentials.credentials

    # 2. Поиск канала
    channel = await Channel.find_one(Channel.token == token)
    if not channel:
        raise HTTPException(status_code=403, detail="Invalid channel token")

    # 3. Отправка запроса в канал
    await send_message_to_channel_logic(channel, data)

    return {"detail": "Message delivered"}
