from datetime import UTC, datetime
from typing import Annotated, Literal

from beanie import Document
from bson import ObjectId
from pydantic import ConfigDict, Field


class Message(Document):
    message_id: Annotated[str, Field(description="ID сообщения, полученного из канала")]
    chat_id: Annotated[str, Field(description="ID чата")]
    text: Annotated[str, Field(description="Текст сообщения")]
    message_sender: Annotated[
        Literal["customer", "employee"], Field(description="Отправитель сообщения"),
    ]
    channel_id: Annotated[ObjectId, Field(description="ID канала")]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(UTC))]

    class Settings:
        name = "messages"

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "message_id": "abc123",
                "chat_id": "chat789",
                "text": "Hello!",
                "message_sender": "customer",
                "channel_id": "66cfe572a2f65b5bd231be1b",
            },
        },
    )
