from enum import StrEnum, auto

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    ASSISTANT = auto()
    SYSTEM = auto()
    USER = auto()


class DialogueMessage(BaseModel):
    role: MessageRole
    text: str


class Dialogue(Document):
    chat_bot_id: PydanticObjectId
    chat_id: str
    message_list: list[DialogueMessage] = Field(default_factory=list)
    processed_message_ids: list[str] = Field(default_factory=list)
