from datetime import datetime, timezone
from beanie import Document, PydanticObjectId, Indexed
from pydantic import BaseModel, HttpUrl, Field, field_validator, ConfigDict
from typing import Literal, Optional

# Database Model
class Channel(Document):
    bot_id: PydanticObjectId = Field(..., description="ID чат-бота в базе данных")
    channel_url: HttpUrl = Field(..., description="URL для отправки сообщений в канал")
    channel_token: str = Field(..., description="Токен авторизации канала")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "channels"
        indexes = [("bot_id",)]

    def __init__(self, **data):  # обновлять updated_at при изменении
        super().__init__(**data)
        self.updated_at = datetime.now(timezone.utc)

# Pydantic Schemas
class ChannelBase(BaseModel):
    channel_url: HttpUrl = Field(..., title="URL канала")
    channel_token: str = Field(..., min_length=8, title="Токен канала")

class ChannelCreate(ChannelBase):
    bot_id: PydanticObjectId = Field(..., title="ID чат-бота")

class ChannelRead(ChannelBase):
    id: PydanticObjectId = Field(..., alias="_id")
    bot_id: PydanticObjectId
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        validate_by_name = True,
        from_attributes = True,
    )

class ChannelUpdate(BaseModel):
    channel_url: Optional[HttpUrl] = Field(None, title="Новый URL канала")
    channel_token: Optional[str] = Field(None, min_length=8, title="Новый токен канала")

    @field_validator("channel_token")
    def token_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Токен не может быть пустым")
        return v
