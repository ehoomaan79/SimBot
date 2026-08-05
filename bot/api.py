import os
import time

import aiohttp

from logger import get_logger
from signer import append_sign

from pathlib import Path

logger = get_logger(__name__)

URL = os.getenv("API_URL")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
        "OPR/133.0.0.0"
    ),
    "Origin": "https://kingshot-giftcode.centurygame.com",
    "Referer": "https://kingshot-giftcode.centurygame.com/",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,fa;q=0.8,fr;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://ks-giftcode.centurygame.com/",
    "sec-ch-ua": '"Opera GX";v="133", "Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site"
}


async def redeem(fid, code, kid):
    timestamp = int(time.time())

    data = {
        "fid": str(fid),
        "cdk": str(code),
        "kid": str(kid),
        "time": str(timestamp),
    }

    payload = append_sign(data)
    logger.debug("Preparing redeem request for fid=%s kid=%s code=%s", fid, kid, code)
    logger.debug("Payload: %s", payload)

    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.post(URL, data=payload) as response:
                logger.info("Redeem request completed with status %s", response.status)
                logger.debug("Response headers: %s", dict(response.headers))
                text = await response.text()
                logger.debug("Raw redeem response: %s", text)
                return text
    except Exception as exc:
        logger.exception("Redeem request failed for fid=%s kid=%s code=%s", fid, kid, code)
        raise