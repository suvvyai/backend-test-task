from beanie import PydanticObjectId

from app.repo.dialogue import IDialogueRepo
from app.service.base import AbstractService
from core.database.models import Dialogue


class DialogueService(AbstractService):
    """Service for dialogues"""

    def __init__(self, repo: IDialogueRepo):
        self.repo = repo

    async def get(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> Dialogue:
        return await self.repo.get(chat_id, chat_bot_id)

    async def create(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> Dialogue:
        return await self.repo.create(chat_id, chat_bot_id)

    async def get_or_create(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> tuple[Dialogue, bool]:
        instance = await self.get(chat_id, chat_bot_id)
        if instance is not None:
            return instance, False

        instance = await self.create(chat_id, chat_bot_id)
        return instance, True
