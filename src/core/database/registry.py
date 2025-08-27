from beanie import init_beanie
from loguru import logger


from core.database.client import get_database
from core.database.models import Channel, ChatBot, Dialogue


async def initialize_database() -> None:
    logger.info("Initialising DB...")

    db = get_database()

    await init_beanie(
        database=db,
        document_models=[
            ChatBot,
            Dialogue,
            Channel,
        ],
    )
    logger.success("DB is ready!")
