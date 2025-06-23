from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class MessageIn(BaseModel):
    message_id: Annotated[str, Field(description="ID сообщения из канала")]
    chat_id: Annotated[str, Field(description="ID чата")]
    text: Annotated[str, Field(description="Текст сообщения")]
    message_sender: Annotated[Literal["customer", "employee"], Field()]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message_id": "abc123",
                "chat_id": "chat789",
                "text": "Hello!",
                "message_sender": "customer",
            },
        },
    )


class MessageSend(BaseModel):
    chat_id: Annotated[str, Field(description="ID чата")]
    text: Annotated[str, Field(description="Текст сообщения")]

    model_config = ConfigDict(
        json_schema_extra={"example": {"chat_id": "chat123", "text": "Hello!"}},
    )


class MessageResponse(BaseModel):
    id: str
    message_id: str
    chat_id: str
    text: str
    message_sender: Literal["customer", "employee"]
    channel_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
