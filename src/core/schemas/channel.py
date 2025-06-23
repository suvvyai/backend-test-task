from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ChannelCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    token: Annotated[str, Field(min_length=10)]
    url: Annotated[HttpUrl, Field()]


class ChannelUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=100)]
    token: Annotated[str | None, Field(default=None, min_length=10)]
    url: Annotated[HttpUrl | None, Field(default=None)]


class ChannelResponse(BaseModel):
    id: str
    name: str
    token: str
    url: HttpUrl
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
