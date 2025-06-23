from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@patch(
    "src.app.routers.api.messages.send_message_to_channel_logic", new_callable=AsyncMock,
)
async def test_send_message_success(mock_send: AsyncMock, client: AsyncClient, init_db: None) -> None:
    # 1. Создание канала
    channel_data = {
        "name": "SendChannel",
        "token": "sendtoken123",
        "url": "https://example.com",
    }
    await client.post("/api/channels/", json=channel_data)

    # 2. Отправка сообщения
    message_data = {"chat_id": "chat-test", "text": "Test message to channel"}
    headers = {"Authorization": f"Bearer {channel_data['token']}"}
    response = await client.post(
        "/api/messages/send", json=message_data, headers=headers,
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail": "Message delivered"}

    # Проверим, что send_message_to_channel_logic действительно вызвался
    assert mock_send.called


@pytest.mark.asyncio
@patch(
    "src.app.routers.api.messages.send_message_to_channel_logic", new_callable=AsyncMock,
)
async def test_send_message_invalid_token(mock_send: AsyncMock, client: AsyncClient, init_db: None) -> None:
    message_data = {"chat_id": "chat-fail", "text": "Unauthorized"}
    headers = {"Authorization": "Bearer wrong-token"}

    response = await client.post(
        "/api/messages/send", json=message_data, headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid channel token"

    # Проверим, что send_message_to_channel_logic не вызывался
    assert not mock_send.called
