import abc

from beanie import PydanticObjectId

from core.database.models.channel import Channel


class IChannelRepo(abc.ABC):
    """Interface for channels repository"""

    @abc.abstractmethod
    async def get(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> Channel:
        """Get channel by chat id and chatbot id"""

    @abc.abstractmethod
    async def create(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
        response_url: str,
        response_token: str,
    ) -> Channel:
        """Create channel by chat id and chatbot id"""

    @abc.abstractmethod
    async def delete(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> None:
        """Delete channel by chat id and chatbot id"""
