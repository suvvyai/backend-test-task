from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from app.routers.api.schemas import ChannelCreate, ChannelRead, ChannelUpdate
from core.database.models import Channel

router = APIRouter(prefix="/channels", tags=["Channels"])


@router.post("/", response_model=ChannelRead, status_code=status.HTTP_201_CREATED)
async def create_channel(channel_in: ChannelCreate) -> Channel:
    """Создание нового канала."""
    channel = Channel(**channel_in.model_dump())
    await channel.insert()
    return channel


@router.get("/", response_model=list[ChannelRead])
async def list_channels() -> list[Channel]:
    """Получение списка всех каналов."""
    channels = await Channel.find_all().to_list()
    return channels


@router.get("/{channel_id}", response_model=ChannelRead)
async def get_channel(channel_id: PydanticObjectId) -> Channel:
    """Получение деталей конкретного канала."""
    channel = await Channel.get(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    return channel


@router.put("/{channel_id}", response_model=ChannelRead)
async def update_channel(
    channel_id: PydanticObjectId,
    channel_update: ChannelUpdate,
) -> Channel:
    """Обновление канала."""
    channel = await get_channel(channel_id)
    update_data = channel_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    await channel.update({"$set": update_data})
    updated_channel = await Channel.get(channel_id)
    return updated_channel


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(channel_id: PydanticObjectId) -> None:
    """Удаление канала."""
    channel = await get_channel(channel_id)
    await channel.delete()
    return
