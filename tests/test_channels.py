from httpx import AsyncClient
from fastapi import status
from core.database.models import ChatBot

async def test_channels_crud_flow(client: AsyncClient) -> None:
    bot = ChatBot(name="bot", secret_token="secret")
    await bot.insert()

    # Create channel
    resp = await client.post(
        "/api/channels/",
        json={
            "name": "test",
            "chat_bot_id": str(bot.id),
            "webhook_url": "http://testserver/api/hello_world/channel_sink",
            "token": "ch_secret",
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    created = resp.json()
    channel_id = created["id"]

    # Get
    resp = await client.get(f"/api/channels/{channel_id}")
    assert resp.status_code == status.HTTP_200_OK

    # List
    resp = await client.get("/api/channels/")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1

    # Update
    resp = await client.patch(
        f"/api/channels/{channel_id}",
        json={"name": "new", "token": "newtok"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "new"

    # Delete
    resp = await client.delete(f"/api/channels/{channel_id}")
    assert resp.status_code == status.HTTP_200_OK


