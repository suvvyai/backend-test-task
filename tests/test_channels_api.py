import pytest
from httpx import AsyncClient, Response
from unittest.mock import MagicMock, AsyncMock

from src.core.database.models import Channel, ChatBot, Dialogue


@pytest.fixture
async def chat_bot() -> ChatBot:
    bot = ChatBot(name="Test Bot", secret_token="test_bot_token_123")
    await bot.insert()
    return bot


@pytest.fixture
async def channel(chat_bot: ChatBot) -> Channel:
    channel = Channel(
        chat_bot_id=chat_bot.id,
        webhook_url="https://example.com/webhook",
        secret_token="channel_secret_123",
    )
    await channel.insert()
    return channel


class TestWebhookAPI:
    async def test_new_message_from_customer(
        self,
        client: AsyncClient,
        chat_bot: ChatBot,
        channel: Channel,
        mocker: MagicMock,
    ):
        message_data = {
            "message_id": "msg_001",
            "chat_id": "chat_123",
            "text": "Hello, I need help!",
            "message_sender": "customer",
        }
        mocker.patch(
            "src.predict.mock_llm_call.mock_llm_call", return_value="Test Response"
        )
        mock_send = mocker.patch(
            "src.app.services.channel_sender.ChannelSenderService.send_message",
            new_callable=AsyncMock,
        )

        response = await client.post(
            "/api/webhook/new_message",
            json=message_data,
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        dialogue = await Dialogue.find_one(
            Dialogue.external_chat_id == message_data["chat_id"]
        )
        assert dialogue is not None
        assert len(dialogue.message_list) == 2
        mock_send.assert_called_once()

    async def test_new_message_from_employee(
        self, client: AsyncClient, chat_bot: ChatBot, mocker: MagicMock
    ):
        message_data = {
            "message_id": "msg_002",
            "chat_id": "chat_123",
            "text": "Internal note",
            "message_sender": "employee",
        }
        mock_send = mocker.patch(
            "src.app.services.channel_sender.ChannelSenderService.send_message"
        )

        response = await client.post(
            "/api/webhook/new_message",
            json=message_data,
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        dialogue = await Dialogue.find_one(
            Dialogue.external_chat_id == message_data["chat_id"]
        )
        assert dialogue is None
        mock_send.assert_not_called()

    async def test_duplicate_message(
        self,
        client: AsyncClient,
        chat_bot: ChatBot,
        channel: Channel,
        mocker: MagicMock,
    ):
        message_data = {
            "message_id": "msg_003",
            "chat_id": "chat_456",
            "text": "Test message",
            "message_sender": "customer",
        }
        mocker.patch(
            "src.predict.mock_llm_call.mock_llm_call", return_value="Test Response"
        )
        mock_send = mocker.patch(
            "src.app.services.channel_sender.ChannelSenderService.send_message",
            new_callable=AsyncMock,
        )

        await client.post(
            "/api/webhook/new_message",
            json=message_data,
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
        )
        await client.post(
            "/api/webhook/new_message",
            json=message_data,
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
        )

        dialogue = await Dialogue.find_one(
            Dialogue.external_chat_id == message_data["chat_id"]
        )
        assert dialogue is not None
        assert len(dialogue.message_list) == 2
        mock_send.assert_called_once()

    async def test_invalid_auth_scheme(self, client: AsyncClient):
        response = await client.post(
            "/api/webhook/new_message",
            json={},
            headers={"Authorization": "Basic token"},
        )
        assert response.status_code == 401
        assert "Invalid authorization scheme" in response.text

    async def test_invalid_token(self, client: AsyncClient):
        response = await client.post(
            "/api/webhook/new_message",
            json={},
            headers={"Authorization": "Bearer invalid"},
        )
        assert response.status_code == 403
        assert "Invalid token" in response.text

    async def test_missing_authorization_header(self, client: AsyncClient):
        valid_payload = {
            "message_id": "msg_006",
            "chat_id": "chat_111",
            "text": "Test",
            "message_sender": "customer",
        }
        response = await client.post("/api/webhook/new_message", json=valid_payload)
        assert response.status_code == 422
        assert "authorization" in response.text
        assert "missing" in response.text

    async def test_context_preservation(
        self,
        client: AsyncClient,
        chat_bot: ChatBot,
        channel: Channel,
        mocker: MagicMock,
    ):
        chat_id = "chat_context_test"
        mocker.patch(
            "src.predict.mock_llm_call.mock_llm_call", return_value="Test Response"
        )
        mock_send = mocker.patch(
            "src.app.services.channel_sender.ChannelSenderService.send_message",
            new_callable=AsyncMock,
        )

        await client.post(
            "/api/webhook/new_message",
            json={
                "message_id": "msg_ctx_001",
                "chat_id": chat_id,
                "text": "My name is John",
                "message_sender": "customer",
            },
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
        )
        await client.post(
            "/api/webhook/new_message",
            json={
                "message_id": "msg_ctx_002",
                "chat_id": chat_id,
                "text": "What is my name?",
                "message_sender": "customer",
            },
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
        )

        dialogue = await Dialogue.find_one(Dialogue.external_chat_id == chat_id)
        assert dialogue is not None
        assert len(dialogue.message_list) == 4
        assert mock_send.call_count == 2

    async def test_multiple_chats_isolation(
        self,
        client: AsyncClient,
        chat_bot: ChatBot,
        channel: Channel,
        mocker: MagicMock,
    ):
        mocker.patch(
            "src.predict.mock_llm_call.mock_llm_call", return_value="Test Response"
        )
        mocker.patch(
            "src.app.services.channel_sender.ChannelSenderService.send_message",
            new_callable=AsyncMock,
        )

        await client.post(
            "/api/webhook/new_message",
            json={
                "message_id": "msg_iso_001",
                "chat_id": "chat_A",
                "text": "For A",
                "message_sender": "customer",
            },
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
        )
        await client.post(
            "/api/webhook/new_message",
            json={
                "message_id": "msg_iso_002",
                "chat_id": "chat_B",
                "text": "For B",
                "message_sender": "customer",
            },
            headers={"Authorization": f"Bearer {chat_bot.secret_token}"},
        )

        dialogue_a = await Dialogue.find_one(Dialogue.external_chat_id == "chat_A")
        dialogue_b = await Dialogue.find_one(Dialogue.external_chat_id == "chat_B")
        assert dialogue_a is not None
        assert dialogue_b is not None
        assert dialogue_a.id != dialogue_b.id
