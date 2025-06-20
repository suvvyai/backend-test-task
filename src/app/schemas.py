from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId


class ChannelCreate(BaseModel):
    bot_id: str
    channel_url: str
    channel_token: str


class ChannelUpdate(BaseModel):
    channel_url: str | None = None
    channel_token: str | None = None


class ChannelRead(BaseModel):
    id: str
    bot_id: str
    channel_url: str
    channel_token: str


class MessageRole(str, Enum):
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    ASSISTANT = "assistant"


class IncomingMessage(BaseModel):
    message_id: str
    chat_id: str
    text: str
    message_sender: MessageRole


class OutgoingMessage(BaseModel):
    # пока не используется, но можно оставить
    event_type: str
    chat_id: str
    text: str


class BotCreate(BaseModel):
    name: str
    secret_token: str


class BotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    name: str
    secret_token: str
