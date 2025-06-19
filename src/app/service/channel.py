import httpx
from beanie import PydanticObjectId

from app.repo.channel import IChannelRepo
from app.routers.schemas.messages import NewMessageRequest
from app.service.base import AbstractService
from core.database.models.channel import Channel


class ChannelService(AbstractService):
    """Service for channels"""

    def __init__(self, repo: IChannelRepo):
        self.repo = repo

    async def get(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> Channel:
        return await self.repo.get(chat_id, chat_bot_id)

    async def create(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
        response_url: str,
        response_token: str,
    ) -> Channel:
        return await self.repo.create(
            chat_id,
            chat_bot_id,
            response_url,
            response_token,
        )

    async def delete(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> None:
        await self.repo.delete(chat_id, chat_bot_id)

    async def send_message(
        self,
        url: str,
        token: str,
        chat_id: str,
        text: str,
    ) -> None:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = NewMessageRequest(
            chat_id=chat_id,
            text=text,
        ).model_dump()

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
