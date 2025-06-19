import abc

from core.database.models import ChatBot


class IChatBotRepo(abc.ABC):
    """Interface for chatbots repository"""

    @abc.abstractmethod
    async def get(self, token: str) -> ChatBot:
        """Get chatbot by token"""
