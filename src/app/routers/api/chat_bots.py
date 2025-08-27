from uuid import uuid4

from beanie import PydanticObjectId
from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict, Field

from core.database.models import ChatBot

router = APIRouter(prefix="/chatbots", tags=["ChatBots"])


class ChatBotCreate(BaseModel):
    name: str


class ChatBotRead(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id")
    name: str
    secret_token: str

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


@router.post("/", response_model=ChatBotRead, status_code=status.HTTP_201_CREATED)
async def create_chat_bot(
    bot_data: ChatBotCreate,
) -> ChatBot:
    """
    Создает нового чат-бота с указанным именем и случайным токеном.
    """
    new_bot = ChatBot(name=bot_data.name, secret_token=str(uuid4()))
    await new_bot.insert()
    return new_bot
