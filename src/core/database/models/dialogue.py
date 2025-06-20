from enum import StrEnum, auto
from datetime import datetime, timezone
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    ASSISTANT = auto()
    SYSTEM = auto()
    USER = "customer"
    EMPLOYEE  = "employee"

class DialogueMessage(BaseModel):
    role: MessageRole
    text: str


class Dialogue(Document):
    """
    Документ диалога, содержащий сообщения и обработанные идентификаторы.
    """
    chat_bot_id: PydanticObjectId = Field(..., description="ID чат-бота в БД")
    message_list: list[DialogueMessage] = Field(default_factory=list, description="Список сообщений диалога")
    processed_message_ids: list[str] = Field(default_factory=list, description="Список ID уже обработанных сообщений")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Время создания диалога")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Время последнего обновления диалога")

    class Settings:
        name = "dialogues"
        indexes = []

    def __init__(self, **data):
        super().__init__(**data)
        # Обновление метки времени при создании/инициализации
        self.updated_at = datetime.now(timezone.utc)
