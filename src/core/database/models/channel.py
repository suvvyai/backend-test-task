from datetime import UTC, datetime
from typing import Annotated

from beanie import Document
from pydantic import ConfigDict, Field, HttpUrl


class Channel(Document):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    url: Annotated[
        HttpUrl, Field(description="URL, на который нужно отправлять сообщения"),
    ]
    token: Annotated[
        str, Field(min_length=1, description="Токен авторизации для отправки сообщений"),
    ]

    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(UTC))]

    class Settings:
        name = "channels"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Telegram Support",
                "url": "https://api.telegram.org/bot1234/sendMessage",
                "token": "secret-token-xyz",
            },
        },
    )
