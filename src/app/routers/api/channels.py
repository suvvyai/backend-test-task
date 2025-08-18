from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Path

from core.database.models import Channel, ChatBot
from core.database.models.schemas import ChannelCreate, ChannelRead, ChannelUpdate


router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", response_model=ChannelRead)
async def create_channel(payload: ChannelCreate) -> ChannelRead:
    chat_bot = await ChatBot.get(payload.chat_bot_id)
    if chat_bot is None:
        raise HTTPException(status_code=404, detail="ChatBot not found")

    channel = Channel(
        name=payload.name,
        chat_bot_id=payload.chat_bot_id,
        settings={
            "webhook_url": str(payload.webhook_url),
            "token": payload.token,
        },
    )
    await channel.insert()
    return ChannelRead(
        id=channel.id,  # type: ignore[arg-type]
        name=channel.name,
        chat_bot_id=channel.chat_bot_id,
        webhook_url=channel.settings.webhook_url,  # type: ignore[attr-defined]
    )


@router.get("/", response_model=list[ChannelRead])
async def list_channels() -> list[ChannelRead]:
    channels = await Channel.find_all().to_list()
    return [
        ChannelRead(
            id=c.id,  # type: ignore[arg-type]
            name=c.name,
            chat_bot_id=c.chat_bot_id,
            webhook_url=c.settings.webhook_url,  # type: ignore[attr-defined]
        )
        for c in channels
    ]


@router.get("/{channel_id}", response_model=ChannelRead)
async def get_channel(channel_id: Annotated[PydanticObjectId, Path()]) -> ChannelRead:
    channel = await Channel.get(channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ChannelRead(
        id=channel.id,  # type: ignore[arg-type]
        name=channel.name,
        chat_bot_id=channel.chat_bot_id,
        webhook_url=channel.settings.webhook_url,  # type: ignore[attr-defined]
    )


@router.patch("/{channel_id}", response_model=ChannelRead)
async def update_channel(channel_id: Annotated[PydanticObjectId, Path()], payload: ChannelUpdate) -> ChannelRead:
    channel = await Channel.get(channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")

    if payload.name is not None:
        channel.name = payload.name
    if payload.webhook_url is not None:
        channel.settings.webhook_url = payload.webhook_url
    if payload.token is not None:
        channel.settings.token = payload.token
    await channel.save()
    return ChannelRead(
        id=channel.id,  # type: ignore[arg-type]
        name=channel.name,
        chat_bot_id=channel.chat_bot_id,
        webhook_url=channel.settings.webhook_url,  # type: ignore[attr-defined]
    )


@router.delete("/{channel_id}")
async def delete_channel(channel_id: Annotated[PydanticObjectId, Path()]) -> dict[str, bool]:
    channel = await Channel.get(channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    await channel.delete()
    return {"success": True}


