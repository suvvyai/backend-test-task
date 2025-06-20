from fastapi import APIRouter, Header, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas import IncomingMessage, MessageRole, OutgoingMessage
from core.database.models.chat_bot import ChatBot
from core.database.models.channel import Channel
from core.database.models.dialogue import Dialogue, DialogueMessage, MessageRole
from app.services.channel_service import post_to_channel
from app.services.llm_service import mock_llm_call

router = APIRouter(prefix="/webhook", tags=["webhook"], dependencies=[Depends(HTTPBearer())])
bearer_scheme = HTTPBearer()


@router.post("/new_message", response_model=OutgoingMessage)
async def receive_webhook(
        msg: IncomingMessage,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """
    chat_id - id чата, берем из channels: "id"
    """
    # 1) Проверяем токен бота
    token = credentials.credentials
    bot = await ChatBot.find_one(ChatBot.secret_token == token)
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен бота",
        )

    # 2) Игнорируем сообщения от сотрудников
    if msg.message_sender == MessageRole.EMPLOYEE:
        return JSONResponse(status_code=200, content={"detail": "Ignored"})

    # 3) Берём или создаём диалог для этого бота
    dlg = await Dialogue.find_one(Dialogue.chat_bot_id == bot.id)
    if not dlg:
        dlg = Dialogue(chat_bot_id=bot.id, processed_message_ids=[], message_list=[])
        await dlg.insert()

    # 4) Проверяем на дубликат
    if msg.message_id in dlg.processed_message_ids:
        return JSONResponse(status_code=409, content={"detail": "Duplicate"})

    # 5) Сохраняем ID пришедшего сообщения и добавляем в историю
    dlg.processed_message_ids.append(msg.message_id)
    dlg.message_list.append(
        DialogueMessage(
            message_id=msg.message_id,
            chat_id=msg.chat_id,
            text=msg.text,
            role=MessageRole.USER,
        )
    )
    await dlg.save()

    # 6) Находим канал для бота
    ch = await Channel.find_one(Channel.bot_id == bot.id)
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")

    # # 7) POST’им во внешний канал
    # await post_to_channel(
    #     str(ch.channel_url),
    #     ch.channel_token,
    #     {"chat_id": msg.chat_id, "text": msg.text},
    # )
    #
    # # 8) Добавляем «ответ» ассистента в историю
    # dlg.message_list.append(
    #     DialogueMessage(
    #         message_id=f"{msg.message_id}-bot",
    #         chat_id=msg.chat_id,
    #         text=msg.text,
    #         role=MessageRole.ASSISTANT,
    #     )
    # )
    # 7) Генерируем ответ через LLM-имитатор
    assistant_response = await mock_llm_call(msg.text, model="echo")

    # 8) Сохраняем ответ ассистента
    dlg.message_list.append(
        DialogueMessage(
            message_id=f"{msg.message_id}-bot",
            chat_id=msg.chat_id,
            text=assistant_response,
            role=MessageRole.ASSISTANT,
        )
    )

    await dlg.save()

    # 9) Возвращаем OK
    return JSONResponse(status_code=200, content={"detail": "OK"})
