from loguru import logger

from app.routers.api.schemas import IncomingMessage
from app.services.channel_sender import ChannelSenderService
from core.database.models import (
    Channel,
    ChatBot,
    Dialogue,
    DialogueMessage,
    MessageRole,
)
from predict.mock_llm_call import mock_llm_call


class MessageHandlerService:
    def __init__(self, chat_bot: ChatBot, message: IncomingMessage):
        self.chat_bot = chat_bot
        self.message = message

    async def process_message(self) -> None:  # <--- Теперь возвращает None
        """
        Основной метод для обработки входящего сообщения.
        Теперь не возвращает текст, а сам вызывает отправку.
        """
        if self.message.message_sender == "employee":
            logger.info(
                f"Ignoring message from employee for chat_id={self.message.chat_id}"
            )
            return

        dialogue = await self._get_or_create_dialogue()

        if self.message.message_id in dialogue.processed_message_ids:
            logger.warning(
                f"Duplicate message_id={self.message.message_id} received. Ignoring."
            )
            return

        dialogue.message_list.append(
            DialogueMessage(role=MessageRole.USER, text=self.message.text)
        )

        response_text = await mock_llm_call(dialogue.message_list)

        dialogue.message_list.append(
            DialogueMessage(role=MessageRole.ASSISTANT, text=response_text)
        )

        dialogue.processed_message_ids.add(self.message.message_id)

        await dialogue.save()
        logger.success(
            f"Processed message and generated response for chat_id={self.message.chat_id}"
        )

        channel = await Channel.find_one(Channel.chat_bot_id == self.chat_bot.id)
        if not channel:
            logger.error(
                f"No channel found for chat_bot_id={self.chat_bot.id}. Cannot send reply."
            )
            return

        await ChannelSenderService.send_message(
            channel=channel, chat_id=self.message.chat_id, text=response_text
        )

    async def _get_or_create_dialogue(self) -> Dialogue:

        dialogue = await Dialogue.find_one(
            Dialogue.chat_bot_id == self.chat_bot.id,
            Dialogue.external_chat_id == self.message.chat_id,
        )
        if not dialogue:
            logger.info(f"Creating new dialogue for chat_id={self.message.chat_id}")
            dialogue = Dialogue(
                chat_bot_id=self.chat_bot.id,
                external_chat_id=self.message.chat_id,
            )
        return dialogue
