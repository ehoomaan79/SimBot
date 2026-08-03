import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


if DISCORD_TOKEN is None:
    raise Exception(
        "DISCORD_TOKEN missing from .env"
    )