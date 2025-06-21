import pytest
from httpx import AsyncClient

from core.database.models.chat_bot import ChatBot
from core.database.models.channel import Channel
from core.database.models.dialogue import Dialogue, MessageRole


# Dummy response для мокирования внешнего HTTP-запроса
def DummyResponse(status_code: int = 200, text: str = "OK") -> object:
    class _:
        def __init__(self) -> None:
            self.status_code = status_code
            self.text = text

    return _()


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient) -> None:
    payload = {"message_id": "1", "chat_id": "chat1", "text": "hello", "message_sender": "customer"}
    # Неправильный токен — ожидаем 401
    response = await client.post(
        "/api/webhook/new_message",
        json=payload,
        headers={"Authorization": "Bearer wrongtoken"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный токен бота"


@pytest.mark.asyncio
async def test_ignore_employee_message(client: AsyncClient) -> None:
    # Сначала создаём бота в БД
    bot = ChatBot(name="Test Bot", secret_token="valid-token")
    await bot.insert()

    payload = {"message_id": "2", "chat_id": "chat2", "text": "ignored", "message_sender": "employee"}
    # Сообщение от сотрудника — должны вернуть 200 и detail="Ignored"
    response = await client.post(
        "/api/webhook/new_message",
        json=payload,
        headers={"Authorization": "Bearer valid-token"},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Ignored"


@pytest.mark.asyncio
async def test_successful_message_processing(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    bot = ChatBot(name="Test Bot", secret_token="valid-token")
    await bot.insert()
    channel = Channel(bot_id=bot.id, channel_url="http://example.com/webhook", channel_token="chan-token")
    await channel.insert()

    # Патчим функцию, а не весь AsyncClient
    import app.services.channel_service as svc

    async def dummy_post_to_channel(url: str, token: str, payload: dict) -> None:
        assert url == "http://example.com/webhook"
        assert token == "chan-token"  # noqa: S105
        assert payload["chat_id"] == "chat3"
        assert payload["text"]
        # возвращать ничего не нужно

    monkeypatch.setattr(svc, "post_to_channel", dummy_post_to_channel)

    payload = {"message_id": "3", "chat_id": "chat3", "text": "hi there", "message_sender": "customer"}
    response = await client.post(
        "/api/webhook/new_message",
        json=payload,
        headers={"Authorization": "Bearer valid-token"},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "OK"

    # Проверяем, что в БД появился диалог с двумя сообщениями
    dialogue = await Dialogue.find_one(Dialogue.chat_bot_id == bot.id)
    assert dialogue is not None
    assert "3" in dialogue.processed_message_ids
    assert len(dialogue.message_list) == 2
    assert dialogue.message_list[0].role == MessageRole.USER
    assert dialogue.message_list[1].role == MessageRole.ASSISTANT


@pytest.mark.asyncio
async def test_duplicate_message_id(client: AsyncClient) -> None:
    # Если сообщение уже обрабатывалось — вернём 409
    bot = ChatBot(name="Test Bot", secret_token="valid-token")
    await bot.insert()
    dialogue = Dialogue(chat_bot_id=bot.id, processed_message_ids=["4"])
    await dialogue.insert()

    payload = {"message_id": "4", "chat_id": "chat4", "text": "duplicate", "message_sender": "customer"}
    response = await client.post(
        "/api/webhook/new_message",
        json=payload,
        headers={"Authorization": "Bearer valid-token"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate"
