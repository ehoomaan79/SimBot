from database import get_gift_channel_id
from giftcodes import process_message
from logger import get_logger


logger = get_logger(__name__)


async def handle_message(message):
    configured_channel_id = get_gift_channel_id()
    if not configured_channel_id:
        logger.debug("No gift-code channel configured yet")
        return

    if str(message.channel.id) != str(configured_channel_id):
        logger.debug("Ignoring message from channel %s; configured channel is %s", message.channel.id, configured_channel_id)
        return

    if getattr(message.author, "bot", False):
        return

    logger.info("Gift-code message received in configured channel %s", message.channel.id)
    logger.debug("Gift-code message content: %s", message.content)
    await process_message(message.content)