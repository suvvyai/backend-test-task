from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from httpx import AsyncClient

from core.database.models import Channel, ChatBot, Dialogue

pytestmark = pytest.mark.asyncio


async def test_new_message_success(
    client: AsyncClient,
    chat_bot: ChatBot,
    channel: Channel,
    mocker: MagicMock,
) -> None:

    mocker.patch(
        "app.services.message_handler.mock_llm_call",
        return_value="Test Response",
    )
    mock_send = mocker.patch(
        "app.services.channel_sender.ChannelSenderService.send_message",
        new_callable=AsyncMock,
    )

    headers = {"Authorization": f"Bearer {chat_bot.secret_token}"}
    payload = {
        "message_id": "msg-webhook-1",
        "chat_id": "chat-webhook-1",
        "text": "Hello!",
        "message_sender": "customer",
    }

    response = await client.post(
        "/api/webhook/new_message",
        headers=headers,
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    dialogue = await Dialogue.find_one(Dialogue.external_chat_id == "chat-webhook-1")
    assert dialogue is not None
    mock_send.assert_called_once()

    kwargs_sent = mock_send.call_args.kwargs
    assert kwargs_sent.get("text") == "Test Response"


async def test_ignore_employee_message(
    client: AsyncClient,
    chat_bot: ChatBot,
    channel: Channel,
    mocker: MagicMock,
) -> None:
    mock_llm = mocker.patch("app.services.message_handler.mock_llm_call")
    mock_send = mocker.patch(
        "app.services.channel_sender.ChannelSenderService.send_message",
    )

    headers = {"Authorization": f"Bearer {chat_bot.secret_token}"}
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
    chat_bot: ChatBot,
    channel: Channel,
    mocker: MagicMock,
) -> None:
    mock_llm = mocker.patch(
        "app.services.message_handler.mock_llm_call",
        return_value="Response",
    )
    mock_send = mocker.patch(
        "app.services.channel_sender.ChannelSenderService.send_message",
        new_callable=AsyncMock,
    )

    headers = {"Authorization": f"Bearer {chat_bot.secret_token}"}  # <--- ИЗМЕНЕНИЕ 2
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
