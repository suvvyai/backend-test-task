from app.repo.channel.base import IChannelRepo
from app.repo.channel.mongo import ChannelRepo as MongoDBChannelRepo

dialogue_repo_map = {
    "mongodb": MongoDBChannelRepo,
}


async def get_channel_repo(key: str) -> IChannelRepo:
    return dialogue_repo_map[key]
