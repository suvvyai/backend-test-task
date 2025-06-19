from beanie import PydanticObjectId

from app.repo.dialogue.base import IDialogueRepo
from core.database.models import Dialogue


class DialogueRepo(IDialogueRepo):
    """MongoDB dialogues Repository"""

    async def get(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> Dialogue:
        return await Dialogue.find_one(
            Dialogue.chat_id == chat_id,
            Dialogue.chat_bot_id == chat_bot_id,
        )

    async def create(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> Dialogue:
        instance = await Dialogue(chat_id=chat_id, chat_bot_id=chat_bot_id)
        await instance.insert()
        return instance
