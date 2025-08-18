from typing import Any

import httpx
from beanie import PydanticObjectId

from core.database.models import Channel


async def send_new_message_to_channels(chat_bot_id: PydanticObjectId, chat_id: str, text: str) -> None:
    channels = await Channel.find(Channel.chat_bot_id == chat_bot_id).to_list()

    for channel in channels:
        headers = {"Authorization": f"Bearer {channel.settings.token}"}
        json_payload: dict[str, Any] = {
            "event_type": "new_message",
            "chat_id": chat_id,
            "text": text,
        }

        # Route in-app test traffic to ASGITransport when targeting the test server
        if str(channel.settings.webhook_url).startswith("http://testserver"):
            # Local import to avoid circular import during application startup
            from app.app import app  # type: ignore

            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
                await client.post(str(channel.settings.webhook_url), headers=headers, json=json_payload)
        else:
            async with httpx.AsyncClient() as client:
                await client.post(str(channel.settings.webhook_url), headers=headers, json=json_payload)


