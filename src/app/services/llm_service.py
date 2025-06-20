import asyncio
import random
from typing import Literal


async def mock_llm_call(prompt: str,
                        model: Literal["echo", "reverse", "dummy"] = "echo",
                        delay: float = 0.1
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
    await asyncio.sleep(delay)

    if model == "reverse":
        return prompt[::-1]
    if model == "dummy":
        return "Здесь мог быть ваш ответ от LLM."
    # по-умолчанию — echo
    return prompt