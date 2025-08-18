from beanie import Document, PydanticObjectId
from pydantic import AnyUrl, BaseModel


class ChannelSettings(BaseModel):
    webhook_url: AnyUrl
    token: str


class Channel(Document):
    name: str
    chat_bot_id: PydanticObjectId
    settings: ChannelSettings


