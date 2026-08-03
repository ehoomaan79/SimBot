import aiohttp
import time
import os

from signer import append_sign

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

    print("Payload:", payload)

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(URL, data=payload) as response:
            print("Status:", response.status)
            print("Response headers:", dict(response.headers))
            text = await response.text()
            return text