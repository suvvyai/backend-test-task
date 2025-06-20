import pytest
from httpx import AsyncClient
from beanie import PydanticObjectId

from core.database.models.chat_bot import ChatBot
from core.database.models.channel import Channel


@pytest.mark.asyncio
async def test_crud_channel(client: AsyncClient):
    # Создаем бота
    bot = ChatBot(name="Test Bot", secret_token="bot-token")
    await bot.insert()

    # 1. Create
    create_payload = {
        "bot_id": str(bot.id),
        "channel_url": "http://example.com/webhook",
        "channel_token": "chan12345"
    }
    create_resp = await client.post("/api/channels/", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert PydanticObjectId(created["id"])  # корректный формат ID
    assert created["bot_id"] == str(bot.id)
    assert created["channel_url"] == create_payload["channel_url"]

    channel_id = created["id"]

    # 2. Read
    read_resp = await client.get(f"/api/channels/{channel_id}")
    assert read_resp.status_code == 200
    read = read_resp.json()
    assert read["id"] == channel_id
    assert read["channel_token"] == create_payload["channel_token"]

    # 3. Update
    update_payload = {"channel_url": "http://example.com/new"}
    update_resp = await client.patch(f"/api/channels/{channel_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["channel_url"] == update_payload["channel_url"]

    # 4. Delete
    delete_resp = await client.delete(f"/api/channels/{channel_id}")
    assert delete_resp.status_code == 204

    # 5. Verify deletion
    notfound_resp = await client.get(f"/api/channels/{channel_id}")
    assert notfound_resp.status_code == 404
