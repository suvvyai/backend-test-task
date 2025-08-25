from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.core import settings

_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    """
    Возвращает "ленивый" синглтон-экземпляр mongo клиента.
    Клиент создается только при первом вызове.
    """
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.mongo.url)
    return _mongo_client


def get_database() -> AsyncIOMotorDatabase:
    """
    Возвращает объект базы данных, используя актуальные настройки.
    """
    client = get_mongo_client()
    return client.get_database(settings.mongo.db_name)
