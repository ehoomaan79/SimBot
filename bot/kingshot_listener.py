from giftcodes import process_message
from logger import get_logger


logger = get_logger(__name__)
KINGSHOT_CHANNEL_ID = 1260478586188730398


async def handle_message(message):
    if message.channel.id != KINGSHOT_CHANNEL_ID:
        logger.debug("Ignoring message from channel %s", message.channel.id)
        return

    logger.info("Kingshot message received in channel %s", message.channel.id)
    logger.debug("Kingshot content: %s", message.content)
    await process_message(message.content)