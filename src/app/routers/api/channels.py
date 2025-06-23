from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from src.core.database.models.channel import Channel
from src.core.schemas.channel import ChannelCreate, ChannelResponse, ChannelUpdate

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_channel(data: ChannelCreate) -> ChannelResponse:
    channel = Channel(**data.model_dump())
    await channel.insert()
    return ChannelResponse(
        id=str(channel.id),
        name=channel.name,
        token=channel.token,
        url=channel.url,
        created_at=channel.created_at,
    )


@router.get("/")
async def list_channels() -> list[ChannelResponse]:
    channels = await Channel.find_all().to_list()
    return [
        ChannelResponse(
            id=str(ch.id),
            name=ch.name,
            token=ch.token,
            url=ch.url,
            created_at=ch.created_at,
        )
        for ch in channels
    ]


@router.get("/{channel_id}")
async def get_channel(channel_id: str) -> ChannelResponse:
    if not ObjectId.is_valid(channel_id):
        raise HTTPException(status_code=400, detail="Invalid channel ID")
    channel = await Channel.get(ObjectId(channel_id))
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ChannelResponse(
        id=str(channel.id),
        name=channel.name,
        token=channel.token,
        url=channel.url,
        created_at=channel.created_at,
    )


@router.patch("/{channel_id}")
async def update_channel(channel_id: str, data: ChannelUpdate) -> ChannelResponse:
    if not ObjectId.is_valid(channel_id):
        raise HTTPException(status_code=400, detail="Invalid channel ID")
    channel = await Channel.get(ObjectId(channel_id))
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(channel, key, value)
    await channel.save()
    return ChannelResponse(
        id=str(channel.id),
        name=channel.name,
        token=channel.token,
        url=channel.url,
        created_at=channel.created_at,
    )


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(channel_id: str) -> None:
    if not ObjectId.is_valid(channel_id):
        raise HTTPException(status_code=400, detail="Invalid channel ID")
    channel = await Channel.get(ObjectId(channel_id))
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    await channel.delete()
    return
