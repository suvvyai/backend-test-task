from typing import Literal

from beanie import PydanticObjectId
from pydantic import AnyUrl, BaseModel


class ChannelCreate(BaseModel):
    name: str
    chat_bot_id: PydanticObjectId
    webhook_url: AnyUrl
    token: str


class ChannelRead(BaseModel):
    id: PydanticObjectId
    name: str
    chat_bot_id: PydanticObjectId
    webhook_url: AnyUrl


class ChannelUpdate(BaseModel):
    name: str | None = None
    webhook_url: AnyUrl | None = None
    token: str | None = None


class IncomingMessage(BaseModel):
    message_id: str
    chat_id: str
    text: str
    message_sender: Literal["customer", "employee"]


