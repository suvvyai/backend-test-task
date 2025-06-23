from unittest.mock import AsyncMock, patch

import pytest
from bson import ObjectId
from fastapi import status
from httpx import AsyncClient

from src.core.database.models import Message


@pytest.mark.asyncio
@patch(
    "src.app.routers.api.webhook.send_message_to_channel_logic", new_callable=AsyncMock,
)
async def test_receive_message_success(mock_send: AsyncMock, client: AsyncClient, init_db: None) -> None:
    # 1. Создание канала
    channel_data = {
        "name": "Test Channel",
        "token": "valid-token",
        "url": "https://example.com/hook",
    }
    await client.post("/api/channels/", json=channel_data)

    # 2. Отправка сообщения
    msg_data = {
        "message_id": "msg123",
        "chat_id": "chatabc",
        "text": "Hello from customer",
        "message_sender": "customer",
    }
    headers = {"Authorization": f"Bearer {channel_data['token']}"}
    response = await client.post(
        "/api/webhook/new_message", json=msg_data, headers=headers,
    )

    assert response.status_code == status.HTTP_201_CREATED

    messages = await Message.find_all().to_list()
    assert len(messages) == 1
    assert messages[0].message_id == msg_data["message_id"]
    assert messages[0].text == msg_data["text"]

    # Проверяем, что send_message_to_channel_logic действительно вызвалась
    assert mock_send.called


@pytest.mark.asyncio
@patch(
    "src.app.routers.api.webhook.send_message_to_channel_logic", new_callable=AsyncMock,
)
async def test_receive_message_duplicate(mock_send: AsyncMock, client: AsyncClient, init_db: None) -> None:
    # 1. Создание канала
    channel_data = {
        "name": "Channel",
        "token": "token12345",
        "url": "https://example.com",
    }
    create_resp = await client.post("/api/channels/", json=channel_data)
    channel_id = create_resp.json()["id"]

    # 2. Вставка сообщения вручную
    from src.core.database.models import Message

    await Message(
        message_id="dupe-msg",
        chat_id="chat1",
        text="Hi",
        message_sender="customer",
        channel_id=ObjectId(channel_id),
    ).insert()

    # 3. Повторная отправка того же сообщения
    headers = {"Authorization": f"Bearer {channel_data['token']}"}
    msg = {
        "message_id": "dupe-msg",
        "chat_id": "chat1",
        "text": "Hi again",
        "message_sender": "customer",
    }
    resp = await client.post("/api/webhook/new_message", json=msg, headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    # Проверим, что send_message_to_channel_logic не вызывался
    assert not mock_send.called


@pytest.mark.asyncio
@patch(
    "src.app.routers.api.webhook.send_message_to_channel_logic", new_callable=AsyncMock,
)
async def test_receive_message_invalid_token(mock_send: AsyncMock, client: AsyncClient, init_db: None) -> None:
    msg = {
        "message_id": "msg999",
        "chat_id": "chat9",
        "text": "Unauthorized message",
        "message_sender": "customer",
    }
    headers = {"Authorization": "Bearer wrong-token"}
    resp = await client.post("/api/webhook/new_message", json=msg, headers=headers)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Проверим, что send_message_to_channel_logic не вызывался
    assert not mock_send.called


@pytest.mark.asyncio
@patch(
    "src.app.routers.api.webhook.send_message_to_channel_logic", new_callable=AsyncMock,
)
async def test_receive_message_from_employee(mock_send: AsyncMock, client: AsyncClient, init_db: None) -> None:
    # 1. Канал
    token1 = "oper-token"
    channel_data = {
        "name": "Operator Channel",
        "token": token1,
        "url": "https://example.com/hook",
    }
    await client.post("/api/channels/", json=channel_data)

    # 2. Сообщение от сотрудника
    msg = {
        "message_id": "msg-op",
        "chat_id": "chat-op",
        "text": "Internal note",
        "message_sender": "employee",
    }
    headers = {"Authorization": f"Bearer {token1}"}
    resp = await client.post("/api/webhook/new_message", json=msg, headers=headers)

    assert resp.status_code == status.HTTP_201_CREATED

    messages = await Message.find_all().to_list()
    assert len(messages) == 1
    assert messages[0].message_sender == "employee"

    # Проверим, что send_message_to_channel_logic не вызывался
    assert not mock_send.called


@pytest.mark.asyncio
@patch(
    "src.app.routers.api.webhook.send_message_to_channel_logic", new_callable=AsyncMock,
)
async def test_receive_message_invalid_sender(mock_send: AsyncMock, client: AsyncClient, init_db: None) -> None:
    # 1. Создание канала
    channel_data = {
        "name": "Test Channel",
        "token": "valid-token-123",
        "url": "https://example.com/hook",
    }
    await client.post("/api/channels/", json=channel_data)

    # 2. Отправка сообщения с недопустимым message_sender
    msg = {
        "message_id": "msg-invalid-sender",
        "chat_id": "chat-wrong",
        "text": "Should fail",
        "message_sender": "admin",
    }
    headers = {"Authorization": f"Bearer {channel_data['token']}"}
    response = await client.post("/api/webhook/new_message", json=msg, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Проверим, что send_message_to_channel_logic не вызывался
    assert not mock_send.called
