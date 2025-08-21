from beanie import Document, PydanticObjectId
from pydantic import HttpUrl, SecretStr


class Channel(Document):
    chat_bot_id: PydanticObjectId
    webhook_url: HttpUrl
    secret_token: SecretStr

    class Settings:
        name = "channels"