import asyncio
from random import randint
from typing import Literal


async def mock_llm_call(
    prompt: str,
    model: Literal["echo", "reverse", "dummy"] = "dummy",
) -> str:
    """
    Простая имитация вызова LLM.

    :param prompt: входной текст от пользователя
    :param model: способ обработки:
        - "echo"    — просто возвращает тот же текст;
        - "reverse" — возвращает текст в обратном порядке;
        - "dummy"   — фиксированный ответ.
    :param delay: искусственная задержка ответа в секундах.
    :return: ответ бота.
    """
    # эмулируем небольшую задержку, как при сетевом запросе
    await asyncio.sleep(randint(1, 5))

    if model == "reverse":
        return prompt[::-1]
    if model == "dummy":
        return "New message from llm"
    # по-умолчанию — echo
    return prompt
