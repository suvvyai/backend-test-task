from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Header, HTTPException

from core.database.models import ChatBot, Dialogue, DialogueMessage, MessageRole
from core.database.models.schemas import IncomingMessage
from predict.mock_llm_call import mock_llm_call
from core.services.sender import send_new_message_to_channels


router = APIRouter(prefix="/webhook", tags=["webhook"])



async def get_bot_from_auth(authorization: Annotated[str | None, Header()] = None) -> ChatBot:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.removeprefix("Bearer ").strip()
    chat_bot = await ChatBot.find_one(ChatBot.secret_token == token)
    if chat_bot is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return chat_bot


@router.post("/new_message")
async def new_message(payload: IncomingMessage, chat_bot: ChatBot = Depends(get_bot_from_auth)) -> dict[str, bool]:
    if payload.message_sender == "employee":
        return {"processed": True}

    dialogue = await Dialogue.find_one({
        "chat_bot_id": chat_bot.id,
        "chat_id": payload.chat_id,
    })
    if dialogue is None:
        dialogue = Dialogue(chat_bot_id=chat_bot.id, chat_id=payload.chat_id, message_list=[], processed_message_ids=[])

    if payload.message_id in dialogue.processed_message_ids:
        return {"processed": True}

    dialogue.message_list.append(DialogueMessage(role=MessageRole.USER, text=payload.text))
    dialogue.processed_message_ids.append(payload.message_id)

    response_text = await mock_llm_call(dialogue.message_list)
    dialogue.message_list.append(DialogueMessage(role=MessageRole.ASSISTANT, text=response_text))
    await dialogue.save()

    await send_new_message_to_channels(chat_bot.id, payload.chat_id, response_text)
    return {"processed": True}


