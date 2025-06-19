import abc

from beanie import PydanticObjectId

from core.database.models import Dialogue


class IDialogueRepo(abc.ABC):
    """Interface for dialogues repository"""

    @abc.abstractmethod
    async def get(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> Dialogue:
        """Get dialogue by chat id and chatbot id"""

    @abc.abstractmethod
    async def create(
        self,
        chat_id: str,
        chat_bot_id: PydanticObjectId,
    ) -> Dialogue:
        """Create dialogue by chat id and chatbot id"""
