from app.repo.chat_bot.base import IChatBotRepo
from core.database.models import ChatBot


class ChatBotRepo(IChatBotRepo):
    """MongoDB Repository for chatbots"""

    async def get(self, token: str) -> ChatBot:
        return await ChatBot.find_one(ChatBot.secret_token == token)
