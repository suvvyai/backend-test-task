import pytest
from httpx import AsyncClient, Response
from unittest.mock import MagicMock, AsyncMock
from fastapi import status

from core.database.models import Channel, ChatBot, Dialogue

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def test_bot_and_channel() -> tuple[ChatBot, Channel]:
    bot = ChatBot(name="Webhook Bot", secret_token="webhook_secret")
    await bot.insert()
    channel = Channel(
        chat_bot_id=bot.id,
        webhook_url="https://fake-channel.com/message",
        secret_token="fake_channel_token",
    )
    await channel.insert()
    return bot, channel


async def test_new_message_success(
    client: AsyncClient,
    test_bot_and_channel: tuple[ChatBot, Channel],
    mocker: MagicMock,
) -> None:
    bot, _ = test_bot_and_channel
    mocker.patch(
        "app.services.message_handler.mock_llm_call", return_value="Test Response"
    )
    mock_send = mocker.patch(
        "app.services.channel_sender.ChannelSenderService.send_message",
        new_callable=AsyncMock,
    )

    headers = {"Authorization": f"Bearer {bot.secret_token}"}
    payload = {
        "message_id": "msg-webhook-1",
        "chat_id": "chat-webhook-1",
        "text": "Hello!",
        "message_sender": "customer",
    }

    response = await client.post(
        "/api/webhook/new_message", headers=headers, json=payload
    )

    assert response.status_code == status.HTTP_200_OK
    dialogue = await Dialogue.find_one(Dialogue.external_chat_id == "chat-webhook-1")
    assert dialogue is not None
    mock_send.assert_called_once()

    kwargs_sent = mock_send.call_args.kwargs
    assert kwargs_sent.get("text") == "Test Response"


async def test_ignore_employee_message(
    client: AsyncClient,
    test_bot_and_channel: tuple[ChatBot, Channel],
    mocker: MagicMock,
) -> None:
    bot, _ = test_bot_and_channel
    mock_llm = mocker.patch("src.predict.mock_llm_call.mock_llm_call")
    mock_send = mocker.patch(
        "src.app.services.channel_sender.ChannelSenderService.send_message"
    )

    headers = {"Authorization": f"Bearer {bot.secret_token}"}
    payload = {
        "message_id": "msg-webhook-2",
        "chat_id": "chat-webhook-2",
        "text": "Employee message",
        "message_sender": "employee",
    }

    await client.post("/api/webhook/new_message", headers=headers, json=payload)

    mock_llm.assert_not_called()
    mock_send.assert_not_called()


async def test_ignore_duplicate_message(
    client: AsyncClient,
    test_bot_and_channel: tuple[ChatBot, Channel],
    mocker: MagicMock,
) -> None:
    bot, _ = test_bot_and_channel
    mock_llm = mocker.patch(
        "app.services.message_handler.mock_llm_call", return_value="Response"
    )
    mock_send = mocker.patch(
        "app.services.channel_sender.ChannelSenderService.send_message",
        new_callable=AsyncMock,
    )

    headers = {"Authorization": f"Bearer {bot.secret_token}"}
    payload = {
        "message_id": "msg-duplicate-webhook",
        "chat_id": "chat-duplicate-webhook",
        "text": "First time",
        "message_sender": "customer",
    }

    await client.post("/api/webhook/new_message", headers=headers, json=payload)
    mock_llm.assert_called_once()
    mock_send.assert_called_once()

    mock_llm.reset_mock()
    mock_send.reset_mock()

    await client.post("/api/webhook/new_message", headers=headers, json=payload)
    mock_llm.assert_not_called()
    mock_send.assert_not_called()
