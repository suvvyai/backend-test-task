import httpx
from fastapi import HTTPException

from src.core.database.models import Channel
from src.core.schemas.message import MessageSend


async def send_message_to_channel_logic(channel: Channel, data: MessageSend) -> None:
    payload = {"event_type": "new_message", "chat_id": data.chat_id, "text": data.text}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=str(channel.url),
                json=payload,
                headers={"Authorization": f"Bearer {channel.token}"},
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502, detail=f"Failed to deliver message: {e!s}",
            )
