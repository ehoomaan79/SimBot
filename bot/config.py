import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

def _prompt_for_value(key, prompt_text, default_value=""):
    existing_value = os.getenv(key)
    if existing_value:
        return existing_value

    print(prompt_text)
    value = input().strip()
    if not value and default_value:
        value = default_value

    if value:
        with ENV_PATH.open("a", encoding="utf-8") as handle:
            handle.write(f"\n{key}={value}")
        os.environ[key] = value

    return value


missing_values = []
for key, prompt_text, default_value in (
    ("DISCORD_TOKEN", "Enter the Discord bot token: ", ""),
    ("SIGN_SECRET", "Enter the Kingshot signing secret [default: mN4!pQs6JrYwV9]: ", "mN4!pQs6JrYwV9"),
    ("API_URL", "Enter the Kingshot API URL [default: https://kingshot-giftcode.centurygame.com/api/gift_code]: ", "https://kingshot-giftcode.centurygame.com/api/gift_code"),
):
    value = os.getenv(key) or _prompt_for_value(key, prompt_text, default_value)
    if not value:
        missing_values.append(key)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if missing_values:
    raise RuntimeError(f"Missing required settings: {', '.join(missing_values)}")

if os.getenv("BOT_SETUP_MODE") == "1":
    print("First-run configuration complete. Exiting setup mode.")
    raise SystemExit(0)