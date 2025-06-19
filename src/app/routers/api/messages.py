from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi import Request as FastAPIRequest
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from app.routers.schemas.messages import Request
from app.service.channel import ChannelService
from app.service.chat_bot import ChatBotService
from app.service.dialogue import DialogueService
from core.database.models import DialogueMessage
from predict.mock_llm_call import mock_llm_call

router = APIRouter()
security = HTTPBearer()


def get_chat_bot_service(request: FastAPIRequest) -> ChatBotService:
    return request.app.state.chat_bot_service


def get_dialogue_service(request: FastAPIRequest) -> DialogueService:
    return request.app.state.dialogue_service


def get_channel_service(request: FastAPIRequest) -> ChannelService:
    return request.app.state.channel_service


@router.post("/webhook/new_message")
async def handle_message_from_channel(
    request: Request,
    chat_bot_service: ChatBotService = Depends(get_chat_bot_service),
    dialogue_service: DialogueService = Depends(get_dialogue_service),
    channel_service: ChannelService = Depends(get_channel_service),
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> None:
    token = credentials.credentials
    chat_bot = await chat_bot_service.get(token)
    if not chat_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="chatbot not found",
        )

    channel = await channel_service.get(
        chat_id=request.chat_id,
        chat_bot_id=chat_bot.id,
    )
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="channel not found",
        )

    dialogue = await dialogue_service.get(
        chat_id=request.chat_id,
        chat_bot_id=chat_bot.id,
    )
    if not dialogue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="dialogue not found",
        )

    dialogue.message_list.append(
        DialogueMessage(role="user", text=request.text),
    )
    await dialogue.save()

    if request.message_sender == "employee":
        raise HTTPException(status_code=status.HTTP_200_OK, detail="ok")

    if dialogue.message_list and len(dialogue.message_list) > 1:
        if dialogue.message_list[-2].text == request.text:
            raise HTTPException(status_code=status.HTTP_200_OK, detail="ok")

    response_text = await mock_llm_call(chat_history=dialogue.message_list)
    if response_text:
        dialogue.message_list.append(
            DialogueMessage(role="assistant", text=response_text),
        )
        await dialogue.save()

        await channel_service.send_message(
            url=channel.response_url,
            token=channel.response_token,
            chat_id=request.chat_id,
            text=response_text,
        )

    raise HTTPException(status_code=status.HTTP_200_OK, detail="ok")
