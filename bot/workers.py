import asyncio
import datetime

from api import redeem
from database import get_active_codes, get_all_players, get_latest_code, remove_code, remove_expired_codes
from logger import get_logger


logger = get_logger(__name__)


async def check_codes():
    while True:
        logger.info("Starting daily gift-code worker cycle")

        code = get_latest_code()
        if code:
            logger.info("Checking latest code %s", code)
            try:
                response = await redeem("0", code, "0")
                logger.debug("Latest code validation response: %s", response)
            except Exception as exc:
                logger.exception("Failed to validate latest code %s", code)

        remove_expired_codes()

        codes = get_active_codes()
        if not codes:
            logger.warning("No active codes available; waiting until next daily cycle")
        else:
            players = get_all_players()
            logger.info("Validating %s active codes for %s players", len(codes), len(players))

            for code in codes:
                try:
                    response = await redeem("0", code, "0")
                except Exception as exc:
                    logger.exception("Validation error for code %s", code)
                    continue

                logger.debug("Validation response for %s: %s", code, response)

                if 'expired' in str(response).lower():
                    remove_code(code)
                    logger.warning("Removed expired code %s", code)

        next_run = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        sleep_seconds = max(1, int((next_run - datetime.datetime.utcnow()).total_seconds()))
        logger.info("Daily gift-code worker cycle complete; sleeping for %s seconds", sleep_seconds)
        await asyncio.sleep(sleep_seconds)