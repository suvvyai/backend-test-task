from beanie import PydanticObjectId
from pydantic import BaseModel, Field, HttpUrl, SecretStr


class ChannelBase(BaseModel):
    """Базовая схема для канала."""
    webhook_url: HttpUrl
    secret_token: SecretStr


class ChannelCreate(ChannelBase):
    """Схема для создания канала."""
    chat_bot_id: PydanticObjectId


class ChannelUpdate(BaseModel):
    """Схема для обновления канала. Все поля опциональны."""
    webhook_url: HttpUrl | None = None
    secret_token: SecretStr | None = None


class ChannelRead(ChannelBase):
    """Схема для отображения канала."""
    id: PydanticObjectId = Field(..., alias="_id")
    chat_bot_id: PydanticObjectId

    class Config:
        from_attributes = True