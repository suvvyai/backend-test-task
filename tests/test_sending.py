from fastapi import APIRouter, Request, status
from httpx import AsyncClient

from app.app import app
from core.database.models import ChatBot


received: list[dict] = []


router = APIRouter()


@router.post("/sink")
async def sink(request: Request) -> dict[str, bool]:
    payload = await request.json()
    received.append(payload)
    return {"ok": True}


app.include_router(router, prefix="/test")


async def test_channel_sends_message(client: AsyncClient) -> None:
    # Create bot and channel pointing to our in-app sink
    bot = ChatBot(name="bot", secret_token="secret")
    await bot.insert()

    resp = await client.post(
        "/api/channels/",
        json={
            "name": "sink",
            "chat_bot_id": str(bot.id),
            "webhook_url": "http://testserver/test/sink",
            "token": "tt",
        },
    )
    assert resp.status_code == status.HTTP_200_OK

    # Send a customer message to webhook → expect assistant message sent to sink
    await client.post(
        "/api/webhook/new_message",
        headers={"Authorization": f"Bearer {bot.secret_token}"},
        json={
            "message_id": "mid-1",
            "chat_id": "c1",
            "text": "hello",
            "message_sender": "customer",
        },
    )

    # mock_llm_call sleeps up to 5s; poll a bit
    for _ in range(15):
        if received:
            break
        import asyncio

        await asyncio.sleep(0.5)

    assert received, "no message received by sink"
    assert received[0]["event_type"] == "new_message"
    assert received[0]["chat_id"] == "c1"
    assert "text" in received[0]


