from beanie import PydanticObjectId

from app.repo.channel.base import IChannelRepo
from core.database.models.channel import Channel


class ChannelRepo(IChannelRepo):
    """MongoDB channels Repository"""

    async def get(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> Channel:
        return await Channel.find_one(
            Channel.chat_id == chat_id,
            Channel.chat_bot_id == chat_bot_id,
        )

    async def create(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
        response_url: str,
        response_token: str,
    ) -> Channel:
        instance = Channel(
            chat_id=chat_id,
            chat_bot_id=chat_bot_id,
            response_url=response_url,
            response_token=response_token,
        )
        await instance.insert()
        return instance

    async def delete(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> None:
        channel = await self.get(chat_id, chat_bot_id)
        if channel:
            await channel.delete()
