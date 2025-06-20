from typing import List
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status, Response

from app.schemas import ChannelCreate, ChannelRead, ChannelUpdate, BotCreate
from core.database.models.chat_bot import ChatBot
from core.database.models.channel import Channel

router = APIRouter(prefix="/channels", tags=["channels"])

@router.post("/", response_model=ChannelRead, status_code=status.HTTP_201_CREATED)
async def create_channel(data: ChannelCreate):
    ch = Channel(**data.model_dump())
    await ch.insert()
    return ChannelRead(
        id=str(ch.id), bot_id=str(ch.bot_id), channel_url=str(ch.channel_url), channel_token=ch.channel_token
    )

@router.get("/", response_model=List[ChannelRead])
async def list_channels():
    all_ch = await Channel.find_all().to_list()
    return [ChannelRead(
        id=str(c.id), bot_id=str(c.bot_id), channel_url=str(c.channel_url), channel_token=c.channel_token
    ) for c in all_ch]

@router.get("/{chan_id}", response_model=ChannelRead)
async def get_channel(chan_id: str):
    c = await Channel.get(PydanticObjectId(chan_id))
    if not c:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ChannelRead(
        id=str(c.id), bot_id=str(c.bot_id), channel_url=str(c.channel_url), channel_token=c.channel_token
    )

@router.patch("/{chan_id}", response_model=ChannelRead)
async def update_channel(chan_id: str, data: ChannelUpdate):
    c = await Channel.get(PydanticObjectId(chan_id))
    if not c:
        raise HTTPException(status_code=404, detail="Channel not found")
    update = data.model_dump(exclude_unset=True)
    for k, v in update.items():
        setattr(c, k, v)
    await c.save()
    return ChannelRead(
        id=str(c.id), bot_id=str(c.bot_id), channel_url=str(c.channel_url), channel_token=c.channel_token
    )

@router.delete("/{chan_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response,)
async def delete_channel(chan_id: str):
    c = await Channel.get(PydanticObjectId(chan_id))
    if not c:
        raise HTTPException(status_code=404, detail="Channel not found")
    await c.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
