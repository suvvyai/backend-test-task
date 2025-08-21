from enum import StrEnum, auto
from typing import Set

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
    external_chat_id: str
    message_list: list[DialogueMessage] = []
    processed_message_ids: Set[str] = Field(default_factory=set)

    class Settings:
        name = "dialogues"
        indexes = [
            "external_chat_id",
        ]