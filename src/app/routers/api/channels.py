from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi import Request as FastAPIRequest
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from app.routers.schemas.channels import CreateRequest, Response
from app.service.channel import ChannelService
from app.service.chat_bot import ChatBotService

router = APIRouter(prefix="/channels")
security = HTTPBearer()


def get_channel_service(request: FastAPIRequest) -> ChannelService:
    return request.app.state.channel_service


def get_chat_bot_service(request: FastAPIRequest) -> ChatBotService:
    return request.app.state.chat_bot_service


@router.post("", response_model=Response)
async def create_channel(
    data: CreateRequest,
    chat_bot_service: ChatBotService = Depends(get_chat_bot_service),
    channel_service: ChannelService = Depends(get_channel_service),
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Response:
    token = credentials.credentials
    chat_bot = await chat_bot_service.get(token)
    if not chat_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="chat bot not found",
        )

    channel = await channel_service.create(
        chat_id=data.chat_id,
        chat_bot_id=chat_bot.id,
        response_url=data.response_url,
        response_token=data.response_token,
    )
    return Response(**channel.model_dump())


@router.get("/{chat_id}", response_model=Response)
async def get_channel(
    chat_id: str,
    chat_bot_service: ChatBotService = Depends(get_chat_bot_service),
    channel_service: ChannelService = Depends(get_channel_service),
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Response:
    token = credentials.credentials
    chat_bot = await chat_bot_service.get(token)
    if not chat_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="chat bot not found",
        )

    channel = await channel_service.get(chat_id, chat_bot.id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="channel not found",
        )
    return Response(**channel.model_dump())


@router.delete("/{chat_id}", status_code=204)
async def delete_channel(
    chat_id: str,
    chat_bot_service: ChatBotService = Depends(get_chat_bot_service),
    channel_service: ChannelService = Depends(get_channel_service),
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> None:
    token = credentials.credentials
    chat_bot = await chat_bot_service.get(token)
    if not chat_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="chat bot not found",
        )

    channel = await channel_service.get(chat_id, chat_bot.id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="channel not found",
        )

    await channel.delete()
    return
