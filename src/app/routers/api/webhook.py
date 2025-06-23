from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.database.models import Channel, Message
from src.core.schemas.message import MessageIn, MessageSend
from src.predict.mock_llm_call import mock_llm_call
from src.services.send import send_message_to_channel_logic

security = HTTPBearer()

router = APIRouter(prefix="/webhook", tags=["messages"])


@router.post("/new_message", status_code=201, response_model=None)
async def receive_message(
    message: MessageIn,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> Response | None:
    # 1. Извлечение токена
    token = credentials.credentials

    # 2. Поиск канала
    channel = await Channel.find_one(Channel.token == token)
    if not channel:
        raise HTTPException(status_code=403, detail="Invalid channel token")

    # 3. Проверка на дубликат
    existing = await Message.find_one(
        {"message_id": message.message_id, "channel_id": channel.id},
    )
    if existing:
        return Response(status_code=204)  # 204 No Content — уже было, не повторяем

    # 4. Сохраняем сообщение
    msg = Message(
        message_id=message.message_id,
        chat_id=message.chat_id,
        text=message.text,
        message_sender=message.message_sender,
        channel_id=channel.id,
        created_at=datetime.now(UTC),
    )
    await msg.insert()

    # 5. Ответ пользователю, если нужно
    if message.message_sender == "customer":
        response_text = await mock_llm_call(message.text)
        await send_message_to_channel_logic(
            channel, MessageSend(chat_id=message.chat_id, text=response_text),
        )

    return None  # 201 Created (без тела)
