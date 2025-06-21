from fastapi import APIRouter, status
from app.schemas import BotCreate, BotRead
from core.database.models.chat_bot import ChatBot

router = APIRouter(prefix="/api/bots", tags=["bots"])


@router.post("/", response_model=BotRead, status_code=201)
async def create_bot(data: BotCreate) -> BotRead:
    """
    Создаёт чат-бота.
    """
    bot = ChatBot(**data.model_dump())
    await bot.insert()
    return bot


@router.get("/", response_model=list[BotRead], status_code=status.HTTP_200_OK)
async def list_bots() -> list[ChatBot]:
    """
    Возвращает список всех чат-ботов.
    """
    return await ChatBot.find_all().to_list()
