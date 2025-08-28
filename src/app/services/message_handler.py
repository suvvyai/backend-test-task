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


async def get_or_create_dialogue(
    chat_bot: ChatBot, message: IncomingMessage,
) -> Dialogue:
    dialogue = await Dialogue.find_one(
        Dialogue.chat_bot_id == chat_bot.id,
        Dialogue.external_chat_id == message.chat_id,
    )
    if not dialogue:
        logger.info(f"Creating new dialogue for chat_id={message.chat_id}")
        dialogue = Dialogue(
            chat_bot_id=chat_bot.id,
            external_chat_id=message.chat_id,
        )
    return dialogue


async def process_message(chat_bot: ChatBot, message: IncomingMessage) -> None:
    if message.message_sender == "employee":
        logger.info(
            f"Ignoring message from employee for chat_id={message.chat_id}",
        )
        return

    dialogue = await get_or_create_dialogue(chat_bot, message)

    if message.message_id in dialogue.processed_message_ids:
        logger.warning(
            f"Duplicate message_id={message.message_id} received. Ignoring.",
        )
        return

    dialogue.message_list.append(
        DialogueMessage(role=MessageRole.USER, text=message.text),
    )

    response_text = await mock_llm_call(dialogue.message_list)

    dialogue.message_list.append(
        DialogueMessage(role=MessageRole.ASSISTANT, text=response_text),
    )

    dialogue.processed_message_ids.add(message.message_id)

    await dialogue.save()
    logger.success(
        f"Processed message and generated response for chat_id={message.chat_id}",
    )

    channel = await Channel.find_one(Channel.chat_bot_id == chat_bot.id)
    if not channel:
        logger.error(
            f"No channel found for chat_bot_id={chat_bot.id}. Cannot send reply.",
        )
        return

    await ChannelSenderService.send_message(
        channel=channel,
        chat_id=message.chat_id,
        text=response_text,
    )
