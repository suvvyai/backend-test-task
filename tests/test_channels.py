import pytest
from fastapi import status
from httpx import AsyncClient

from src.core.database.models import Channel


@pytest.mark.asyncio
async def test_create_channel(client: AsyncClient, init_db: None) -> None:
    data = {
        "name": "Test Channel",
        "token": "supersecrettoken",
        "url": "https://example.com/webhook",
    }

    response = await client.post("/api/channels/", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    json_data = response.json()

    assert json_data["name"] == data["name"]
    assert json_data["token"] == data["token"]
    assert json_data["url"] == data["url"]

    channels = await Channel.find_all().to_list()
    assert len(channels) == 1
    assert channels[0].name == data["name"]


@pytest.mark.asyncio
async def test_get_channels(client: AsyncClient, init_db: None) -> None:
    data = {
        "name": "Another Channel",
        "token": "tokentokentoken",
        "url": "https://example.com/hook",
    }
    await client.post("/api/channels/", json=data)

    response = await client.get("/api/channels/")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["name"] == data["name"]


@pytest.mark.asyncio
async def test_update_channel(client: AsyncClient, init_db: None) -> None:
    create_data = {
        "name": "Channel to Update",
        "token": "token9999999",
        "url": "https://example.com/original",
    }
    create_response = await client.post("/api/channels/", json=create_data)
    channel_id = create_response.json()["id"]

    new_name = "Updated Name"
    patch_response = await client.patch(
        f"/api/channels/{channel_id}", json={"name": new_name},
    )
    assert patch_response.status_code == status.HTTP_200_OK
    data = patch_response.json()
    assert data["name"] == new_name

    updated = await Channel.get(channel_id)
    assert updated is not None
    assert updated.name == new_name


@pytest.mark.asyncio
async def test_delete_channel(client: AsyncClient, init_db: None) -> None:
    data = {
        "name": "To Delete",
        "token": "tokentodelete",
        "url": "https://example.com/delete",
    }
    create_response = await client.post("/api/channels/", json=data)
    channel_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/channels/{channel_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    deleted = await Channel.get(channel_id)
    assert deleted is None
