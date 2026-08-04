import asyncio
import datetime
import re

from api import redeem
from database import add_code, get_all_players, remove_code
from logger import get_logger
from reponse_parser import validate_redeem_response


logger = get_logger(__name__)

CODE_BACKTICK_RE = re.compile(r"`([^`]+)`")
GIFT_LABEL_RE = re.compile(r"Gift Code[:\s]*([A-Za-z0-9_-]+)", re.IGNORECASE)
VALID_UNTIL_RE = re.compile(r"Valid Until[:\s]*(.+)", re.IGNORECASE)


def parse_expiry(text):
    """Parse expiry text like 'July 14th, 23:59 (UTC+0)'. Returns unix timestamp (int) or None."""

    if not text:
        return None

    tz_match = re.search(r"\(UTC([+-]?\d+)\)", text)
    tz_offset = 0
    if tz_match:
        try:
            tz_offset = int(tz_match.group(1))
        except ValueError:
            tz_offset = 0

    cleaned = re.sub(r"\(.*?\)", "", text).strip()

    parts = cleaned.split(',')
    if len(parts) >= 2:
        month_day = parts[0].strip()
        time_part = parts[1].strip()
    else:
        tokens = cleaned.split()
        month_day = ' '.join(tokens[:2]) if len(tokens) >= 2 else tokens[0]
        time_part = tokens[-1]

    month_day = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", month_day)

    try:
        month_name, day = month_day.split()
        day = int(day)
    except Exception:
        return None

    try:
        hour_min = time_part.strip()
        hour, minute = [int(x) for x in hour_min.split(':')]
    except Exception:
        hour, minute = 23, 59

    now = datetime.datetime.utcnow()
    month_map = {
        m: i for i, m in enumerate(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            start=1,
        )
    }
    month = month_map.get(month_name, None)
    if month is None:
        month = month_map.get(month_name.capitalize())
    if not month:
        return None

    year = now.year
    dt = datetime.datetime(year, month, day, hour, minute, tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=tz_offset)

    if dt < now.replace(tzinfo=datetime.timezone.utc):
        try:
            dt = datetime.datetime(year + 1, month, day, hour, minute, tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=tz_offset)
        except Exception:
            pass

    return int(dt.timestamp())


def extract_codes(message):
    """Return list of codes found in the message."""
    codes = []

    for m in CODE_BACKTICK_RE.finditer(message):
        codes.append(m.group(1).strip())

    if not codes:
        for m in GIFT_LABEL_RE.finditer(message):
            codes.append(m.group(1).strip())

    return list(dict.fromkeys(codes))


def extract_expiry(message):
    m = VALID_UNTIL_RE.search(message)
    if not m:
        return None
    return parse_expiry(m.group(1).strip())


async def redeem_code_for_players(code, players=None):
    if players is None:
        players = get_all_players()

    if not players:
        logger.info("No players available for redemption of code %s", code)
        return 0

    logger.info("Starting redemption for code %s across %s player(s)", code, len(players))
    sem = asyncio.Semaphore(10)

    async def redeem_for_player(fid, kid):
        async with sem:
            try:
                logger.debug("Redeeming code %s for player %s/%s", code, fid, kid)
                resp = await redeem(fid, code, kid)
            except Exception as exc:
                logger.exception("Redeem error for code %s player %s", code, fid)
                return False

            valid = validate_redeem_response(resp)
            if not valid and 'expired' in str(resp).lower():
                remove_code(code)
                logger.warning("Removed expired code %s", code)
                return False

            if valid:
                logger.info("Redeem succeeded for code %s player %s", code, fid)
                return True

            logger.warning("Redeem failed for code %s player %s. Response: %s", code, fid, resp)
            return False

    tasks = [redeem_for_player(fid, kid) for fid, kid in players]
    results = await asyncio.gather(*tasks) if tasks else []
    return sum(1 for success in results if success)


async def redeem_all_active_codes_for_player(fid, kid):
    players = [(fid, kid)]
    active_codes = [code for code in []]
    from database import get_active_codes

    active_codes = get_active_codes()
    logger.info("Redeeming %s active code(s) for new player %s", len(active_codes), fid)
    successes = 0
    for code in active_codes:
        successes += await redeem_code_for_players(code, players=players)
    return successes


async def process_message(message):
    logger.info("Processing Kingshot gift-code message")
    logger.debug("Message content: %s", message)

    codes = extract_codes(message)
    expires_at = extract_expiry(message)

    logger.info("Extracted %s code(s) and expiry=%s", len(codes), expires_at)

    if not codes:
        logger.warning("No gift codes found in message")
        return

    players = get_all_players()
    logger.info("Found %s registered players for redemption", len(players))

    for code in codes:
        added = add_code(code, expires_at=expires_at)
        if added:
            logger.info("New code stored: %s expires_at=%s", code, expires_at)
            await redeem_code_for_players(code, players=players)
