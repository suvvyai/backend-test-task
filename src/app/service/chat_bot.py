from app.repo.chat_bot.base import IChatBotRepo
from app.service.base import AbstractService
from core.database.models import ChatBot


class ChatBotService(AbstractService):
    """Service for chatbots"""

    def __init__(self, repo: IChatBotRepo):
        self.repo = repo

    async def get(self, token: str) -> ChatBot:
        return await self.repo.get(token)

    async def create(self, *args, **kwargs):
        pass
