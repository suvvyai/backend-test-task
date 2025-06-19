from app.repo.chat_bot.base import IChatBotRepo
from app.repo.chat_bot.mongo import ChatBotRepo as MongoDBChatBotRepo

chat_bot_repo_map = {
    "mongodb": MongoDBChatBotRepo,
}


async def get_chat_bot_repo(key: str) -> IChatBotRepo:
    return chat_bot_repo_map[key]
