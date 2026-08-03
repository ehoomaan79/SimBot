import aiohttp
import os

from signer import append_sign


URL = os.getenv("API_URL")


async def redeem(fid, code, kid):

    data = {
        "fid": fid,
        "cdk": code,
        "kid": kid,
        "time": int(__import__("time").time())
    }


    payload = append_sign(data)


    async with aiohttp.ClientSession() as session:

        async with session.post(
            URL,
            data=payload
        ) as response:

            return await response.text()