import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.repo.channel import get_channel_repo
from app.repo.chat_bot import get_chat_bot_repo
from app.repo.dialogue import get_dialogue_repo
from app.routers import router as main_router
from app.service.channel import ChannelService
from app.service.chat_bot import ChatBotService
from app.service.dialogue import DialogueService
from core import settings
from core.database import initialize_database

load_dotenv()
print(os.environ.get("SERVER__DB_TYPE"))
print(os.environ.get("MONGO__URL"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await initialize_database()

    #  Initializing chatbots service
    chat_bot_repo = await get_chat_bot_repo(settings.db_type)
    chat_bot_service = ChatBotService(chat_bot_repo())
    app.state.chat_bot_service = chat_bot_service

    #  Initializing dialogues service
    dialogue_repo = await get_dialogue_repo(settings.db_type)
    dialogue_service = DialogueService(dialogue_repo())
    app.state.dialogue_service = dialogue_service

    #  Initializing channels service
    channel_repo = await get_channel_repo(settings.db_type)
    channel_service = ChannelService(channel_repo())
    app.state.channel_service = channel_service

    yield


app = FastAPI(
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def index_to_docs_redirect() -> RedirectResponse:
    return RedirectResponse(url="docs")


app.include_router(main_router)
