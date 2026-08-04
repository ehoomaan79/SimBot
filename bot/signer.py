from hashlib import md5
from urllib.parse import quote
import os


SECRET = os.getenv("SIGN_SECRET")


def append_sign(data: dict):

    keys = sorted(data.keys())

    query = "&".join(
        f"{k}={quote(str(data[k]), safe='')}"
        for k in keys
    )

    sign = md5(
        (query + SECRET).encode()
    ).hexdigest()

    return {
        "sign": sign,
        **data
    }