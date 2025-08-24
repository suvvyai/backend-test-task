import httpx
from loguru import logger

from core.database.models import Channel


class ChannelSenderService:
    @staticmethod
    async def send_message(channel: Channel, chat_id: str, text: str) -> None:
        """
        Отправляет сообщение в канал асинхронно.
        """
        url = str(channel.webhook_url)
        token = channel.secret_token.get_secret_value()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "event_type": "new_message",
            "chat_id": chat_id,
            "text": text,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=10.0
                )
                response.raise_for_status()
                logger.success(
                    f"Successfully sent message to chat_id={chat_id} via channel {channel.id}"
                )
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error occurred when sending message to {url}: "
                    f"status_code={e.response.status_code}, response={e.response.text}"
                )
            except httpx.RequestError as e:
                logger.error(
                    f"Request error occurred when sending message to {url}: {e}"
                )
