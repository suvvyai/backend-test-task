from fastapi import status
from httpx import AsyncClient

from core.database.models import ChatBot, Dialogue


async def setup_bot() -> ChatBot:
    bot = ChatBot(name="bot", secret_token="secret")
    await bot.insert()
    return bot


async def test_webhook_ignores_employee_and_dedup(client: AsyncClient) -> None:
    bot = await setup_bot()

    # Employee message ignored
    resp = await client.post(
        "/api/webhook/new_message",
        headers={"Authorization": f"Bearer {bot.secret_token}"},
        json={
            "message_id": "1",
            "chat_id": "chat-1",
            "text": "hello",
            "message_sender": "employee",
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    d = await Dialogue.find_one(Dialogue.chat_id == "chat-1")
    assert d is None

    # Customer message creates dialogue
    resp = await client.post(
        "/api/webhook/new_message",
        headers={"Authorization": f"Bearer {bot.secret_token}"},
        json={
            "message_id": "2",
            "chat_id": "chat-1",
            "text": "hi",
            "message_sender": "customer",
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    d = await Dialogue.find_one(Dialogue.chat_id == "chat-1")
    assert d is not None
    assert "2" in d.processed_message_ids

    # Duplicate message id is ignored
    resp = await client.post(
        "/api/webhook/new_message",
        headers={"Authorization": f"Bearer {bot.secret_token}"},
        json={
            "message_id": "2",
            "chat_id": "chat-1",
            "text": "hi",
            "message_sender": "customer",
        },
    )
    assert resp.status_code == status.HTTP_200_OK


