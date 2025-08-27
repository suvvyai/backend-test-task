import pytest
from httpx import AsyncClient
from beanie import PydanticObjectId
from core.database.models import Channel, ChatBot

pytestmark = pytest.mark.asyncio


async def test_create_chat_bot(client: AsyncClient):
    bot_data = {"name": "My Test Bot"}
    response = await client.post("/api/chatbots/", json=bot_data)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == bot_data["name"]
    assert "_id" in response_data
    assert "secret_token" in response_data
    assert len(response_data["secret_token"]) > 10

    created_bot = await ChatBot.get(response_data["_id"])
    assert created_bot is not None
    assert created_bot.name == bot_data["name"]
    assert created_bot.secret_token == response_data["secret_token"]


async def test_create_chat_bot_no_name(client: AsyncClient):
    response = await client.post("/api/chatbots/", json={})
    assert response.status_code == 422

    error_detail = response.json()
    assert "detail" in error_detail


async def test_create_chat_bot_invalid_data(client: AsyncClient):
    bot_data = {"name": None}
    response = await client.post("/api/chatbots/", json=bot_data)
    assert response.status_code == 422


async def test_create_channel(client: AsyncClient, chat_bot: ChatBot):
    channel_data = {
        "webhook_url": "https://example.com/webhook",
        "secret_token": "secret_token_123",
        "chat_bot_id": str(chat_bot.id),
    }

    response = await client.post("/api/channels/", json=channel_data)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["webhook_url"] == channel_data["webhook_url"]
    assert "secret_token" in response_data
    assert response_data["chat_bot_id"] == channel_data["chat_bot_id"]
    assert "_id" in response_data

    created_channel = await Channel.get(response_data["_id"])
    assert created_channel is not None
    assert str(created_channel.chat_bot_id) == channel_data["chat_bot_id"]


async def test_create_channel_invalid_bot_id(client: AsyncClient):
    channel_data = {
        "webhook_url": "https://example.com/webhook",
        "secret_token": "secret_token_123",
        "chat_bot_id": str(PydanticObjectId()),
    }

    response = await client.post("/api/channels/", json=channel_data)

    assert response.status_code in [201, 400, 422]


async def test_create_channel_invalid_webhook_url(
    client: AsyncClient, chat_bot: ChatBot
):
    channel_data = {
        "webhook_url": "not-a-valid-url",
        "secret_token": "secret_token_123",
        "chat_bot_id": str(chat_bot.id),
    }

    response = await client.post("/api/channels/", json=channel_data)
    assert response.status_code == 422


async def test_create_channel_missing_required_fields(client: AsyncClient):
    incomplete_data = {
        "webhook_url": "https://example.com/webhook",
    }

    response = await client.post("/api/channels/", json=incomplete_data)
    assert response.status_code == 422


async def test_list_channels(client: AsyncClient, channel: Channel):
    response = await client.get("/api/channels/")

    assert response.status_code == 200
    channels_list = response.json()
    assert isinstance(channels_list, list)
    assert len(channels_list) >= 1
    assert str(channel.id) in [c["_id"] for c in channels_list]


async def test_list_channels_empty(client: AsyncClient):
    response = await client.get("/api/channels/")

    assert response.status_code == 200
    channels_list = response.json()
    assert isinstance(channels_list, list)


async def test_get_channel(client: AsyncClient, channel: Channel):
    response = await client.get(f"/api/channels/{channel.id}")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["_id"] == str(channel.id)
    assert response_data["webhook_url"] == str(channel.webhook_url)
    assert "secret_token" in response_data
    assert response_data["chat_bot_id"] == str(channel.chat_bot_id)


async def test_get_channel_not_found(client: AsyncClient):
    non_existent_id = PydanticObjectId()
    response = await client.get(f"/api/channels/{non_existent_id}")

    assert response.status_code == 404
    error_detail = response.json()
    assert "not found" in error_detail["detail"].lower()


async def test_get_channel_invalid_id_format(client: AsyncClient):
    invalid_id = "invalid-id-format"
    response = await client.get(f"/api/channels/{invalid_id}")

    assert response.status_code == 422


async def test_update_channel(client: AsyncClient, channel: Channel):
    update_data = {
        "webhook_url": "https://updated-example.com/webhook",
        "secret_token": "updated_secret_123",
    }

    response = await client.put(f"/api/channels/{channel.id}", json=update_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["webhook_url"] == update_data["webhook_url"]
    assert "secret_token" in response_data

    updated_channel = await Channel.get(channel.id)
    assert str(updated_channel.webhook_url) == update_data["webhook_url"]


async def test_update_channel_partial(client: AsyncClient, channel: Channel):
    update_data = {"webhook_url": "https://partial-update.com/webhook"}
    original_secret = channel.secret_token

    response = await client.put(f"/api/channels/{channel.id}", json=update_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["webhook_url"] == update_data["webhook_url"]
    assert "secret_token" in response_data


async def test_update_channel_not_found(client: AsyncClient):
    non_existent_id = PydanticObjectId()
    update_data = {"webhook_url": "https://example.com/webhook"}

    response = await client.put(f"/api/channels/{non_existent_id}", json=update_data)
    assert response.status_code == 404


async def test_delete_channel(client: AsyncClient, channel: Channel):
    channel_id = channel.id

    delete_response = await client.delete(f"/api/channels/{channel_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/channels/{channel_id}")
    assert get_response.status_code == 404


async def test_delete_channel_not_found(client: AsyncClient):
    non_existent_id = PydanticObjectId()

    response = await client.delete(f"/api/channels/{non_existent_id}")
    assert response.status_code == 404


async def test_channel_chatbot_relationship(client: AsyncClient, chat_bot: ChatBot):
    channel_data = {
        "webhook_url": "https://example.com/webhook",
        "secret_token": "secret_token_123",
        "chat_bot_id": str(chat_bot.id),
    }

    create_response = await client.post("/api/channels/", json=channel_data)
    assert create_response.status_code == 201
    channel_id = create_response.json()["_id"]

    get_response = await client.get(f"/api/channels/{channel_id}")
    assert get_response.status_code == 200

    channel_data = get_response.json()
    assert channel_data["chat_bot_id"] == str(chat_bot.id)


async def test_create_multiple_channels_same_bot(
    client: AsyncClient, chat_bot: ChatBot
):
    channels_data = [
        {
            "webhook_url": f"https://example{i}.com/webhook",
            "secret_token": f"secret_token_{i}",
            "chat_bot_id": str(chat_bot.id),
        }
        for i in range(3)
    ]

    created_channels = []
    for channel_data in channels_data:
        response = await client.post("/api/channels/", json=channel_data)
        assert response.status_code == 201
        created_channels.append(response.json())

    list_response = await client.get("/api/channels/")
    assert list_response.status_code == 200

    channels_list = list_response.json()
    created_ids = [c["_id"] for c in created_channels]
    list_ids = [c["_id"] for c in channels_list]

    for channel_id in created_ids:
        assert channel_id in list_ids


async def test_large_webhook_url(client: AsyncClient, chat_bot: ChatBot):
    long_url = "https://example.com/" + "a" * 2000 + "/webhook"

    channel_data = {
        "webhook_url": long_url,
        "secret_token": "secret_token_123",
        "chat_bot_id": str(chat_bot.id),
    }

    response = await client.post("/api/channels/", json=channel_data)

    assert response.status_code in [201, 422]


async def test_concurrent_channel_creation(client: AsyncClient, chat_bot: ChatBot):
    import asyncio

    async def create_channel(index):
        channel_data = {
            "webhook_url": f"https://concurrent{index}.com/webhook",
            "secret_token": f"concurrent_secret_{index}",
            "chat_bot_id": str(chat_bot.id),
        }
        return await client.post("/api/channels/", json=channel_data)

    tasks = [create_channel(i) for i in range(5)]
    responses = await asyncio.gather(*tasks)

    for response in responses:
        assert response.status_code == 201
