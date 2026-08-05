import asyncio
import datetime

from api import redeem
from database import get_active_codes, get_all_players, get_latest_code, remove_code, remove_expired_codes
from logger import get_logger
from reponse_parser import classify_redeem_response


logger = get_logger(__name__)


async def check_codes():
    while True:
        logger.info("Starting daily gift-code worker cycle")

        code = get_latest_code()
        if code:
            logger.info("Checking latest code %s", code)
            try:
                # Use a test player to validate the code - we need a valid player to check code status
                players = get_all_players()
                if players:
                    test_fid, test_kid = players[0]
                    response = await redeem(test_fid, code, test_kid)
                    logger.debug("Latest code validation response: %s", response)
                    result = classify_redeem_response(response)
                    if result["reason"] == "code_expired":
                        remove_code(code)
                        logger.warning("Removed expired code %s", code)
                else:
                    logger.warning("No players available to validate code %s", code)
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
                    if players:
                        test_fid, test_kid = players[0]
                        response = await redeem(test_fid, code, test_kid)
                    else:
                        logger.warning("No players available to validate code %s", code)
                        continue
                except Exception as exc:
                    logger.exception("Validation error for code %s", code)
                    continue

                logger.debug("Validation response for %s: %s", code, response)
                result = classify_redeem_response(response)

                if result["reason"] == "code_expired":
                    remove_code(code)
                    logger.warning("Removed expired code %s", code)

        next_run = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        sleep_seconds = max(1, int((next_run - datetime.datetime.utcnow()).total_seconds()))
        logger.info("Daily gift-code worker cycle complete; sleeping for %s seconds", sleep_seconds)
        await asyncio.sleep(sleep_seconds)
