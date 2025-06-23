from asyncio import sleep
from random import randint


async def mock_llm_call(prompt: str) -> str:
    await sleep(randint(1, 5))
    return "New message from llm"
