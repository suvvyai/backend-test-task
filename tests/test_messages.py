from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from starlette import status

from core.database.models import ChatBot, Dialogue, DialogueMessage
from core.database.models.channel import Channel


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message_sender, text, should_call",
    [
        ("customer", "Hello", True),
        ("employee", "Hello from employee", False),
    ],
)
async def test_handle_message_from_channel(
    client: AsyncClient,
    chat_bot: ChatBot,
    channel: Channel,
    dialogue: Dialogue,
    message_sender: str,
    text: str,
    should_call: bool,
) -> None:
    with patch(
        "app.service.channel.ChannelService.send_message",
        new_callable=AsyncMock,
    ) as mock_send:
        response = await client.post(
            "/api/webhook/new_message",
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
            json={
                "message_id": "1",
                "chat_id": channel.chat_id,
                "text": text,
                "message_sender": message_sender,
            },
        )
        assert response.status_code == status.HTTP_200_OK

        if should_call:
            mock_send.assert_awaited_once_with(
                url=channel.response_url,
                token=channel.response_token,
                chat_id=channel.chat_id,
                text="New message from llm",
            )
        else:
            mock_send.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_message_from_channel_repeated_text(
    client: AsyncClient,
    chat_bot: ChatBot,
    channel: Channel,
    dialogue: Dialogue,
) -> None:
    dialogue.message_list.append(DialogueMessage(role="user", text="Hello"))
    await dialogue.save()

    with patch(
        "app.service.channel.ChannelService.send_message",
        new_callable=AsyncMock,
    ) as mock_send:
        response = await client.post(
            "/api/webhook/new_message",
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
            json={
                "message_id": "2",
                "chat_id": channel.chat_id,
                "text": "Hello",
                "message_sender": "customer",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        mock_send.assert_not_awaited()
