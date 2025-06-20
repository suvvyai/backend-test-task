import asyncio
import httpx


async def post_to_channel(url: str, token: str, payload: dict) -> None:
    """
    POST’ит payload в канал по URL с нужным заголовком.
    """
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        await client.post(str(url), headers=headers, json=payload)
