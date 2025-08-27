from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.routers.api.schemas import IncomingMessage
from app.services.message_handler import MessageHandlerService
from core.database.models import ChatBot

router = APIRouter(prefix="/webhook", tags=["Webhook"])


async def get_chat_bot_from_token(
    authorization: str = Header(..., description="Bearer <токен чат-бота>"),
) -> ChatBot:
    """Зависимость для аутентификации по токену чат-бота."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
        )
    token = authorization.split(" ")[1]
    chat_bot = await ChatBot.find_one({"secret_token": token})
    if not chat_bot:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )
    return chat_bot


@router.post("/new_message")
async def new_message(
    message: IncomingMessage,
    chat_bot: ChatBot = Depends(get_chat_bot_from_token),
) -> dict:
    """
    Эндпоинт для получения новых сообщений из канала.
    """
    service = MessageHandlerService(chat_bot, message)
    response_text = await service.process_message()

    if response_text:
        print(f"Нужно отправить ответ: '{response_text}' в чат {message.chat_id}")

    return {"status": "ok"}
