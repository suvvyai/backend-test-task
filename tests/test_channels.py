import pytest
from httpx import AsyncClient
from starlette import status

from core.database.models import ChatBot
from core.database.models.channel import Channel


@pytest.mark.asyncio
async def test_create_channel(client: AsyncClient, chat_bot: ChatBot) -> None:
    response = await client.post(
        "/api/channels",
        headers={
            "Authorization": f"Bearer {chat_bot.secret_token}",
        },
        json={
            "chat_id": "test_chat",
            "response_url": "http://example.com",
            "response_token": "channel_token",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["chat_id"] == "test_chat"


@pytest.mark.asyncio
async def test_get_channel(
    client: AsyncClient,
    chat_bot: ChatBot,
    channel: Channel,
) -> None:
    response = await client.get(
        f"/api/channels/{channel.chat_id}",
        headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["chat_id"] == channel.chat_id


@pytest.mark.asyncio
async def test_delete_channel(
    client: AsyncClient,
    chat_bot: ChatBot,
    channel: Channel,
) -> None:
    response = await client.delete(
        f"/api/channels/{channel.chat_id}",
        headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_create_channel_with_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/channels",
        headers={"Authorization": "Bearer invalid_token"},
        json={
            "chat_id": "test_chat",
            "response_url": "http://example.com",
            "response_token": "channel_token",
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "chat bot not found"


@pytest.mark.asyncio
async def test_create_channel_with_missing_fields(
    client: AsyncClient,
    chat_bot: ChatBot,
) -> None:
    response = await client.post(
        "/api/channels",
        headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
        json={
            "chat_id": "test_chat",
            "response_token": "channel_token",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_channel_with_invalid_token(client: AsyncClient, channel: Channel) -> None:
    response = await client.get(
        f"/api/channels/{channel.chat_id}",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "chat bot not found"


@pytest.mark.asyncio
async def test_get_nonexistent_channel(client: AsyncClient, chat_bot: ChatBot) -> None:
    response = await client.get(
        "/api/channels/nonexistent_chat_id",
        headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "channel not found"


@pytest.mark.asyncio
async def test_delete_channel_with_invalid_token(client: AsyncClient, channel: Channel) -> None:
    response = await client.delete(
        f"/api/channels/{channel.chat_id}",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "chat bot not found"


@pytest.mark.asyncio
async def test_delete_nonexistent_channel(
    client: AsyncClient,
    chat_bot: ChatBot,
) -> None:
    response = await client.delete(
        "/api/channels/nonexistent_chat_id",
        headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "channel not found"
