import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_log_path() -> Path:
    configured = os.getenv("DISCORD_BOT_LOG_DIR")
    if configured:
        candidate = Path(configured)
        if not candidate.is_absolute():
            candidate = BASE_DIR / candidate
        return candidate

    for candidate in (
        Path("/var/log/discord-bot"),
        Path("/var/log"),
        Path.home() / "logs",
        BASE_DIR / "logs",
        Path("/tmp"),
    ):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            test_file = candidate / ".write-test"
            with test_file.open("a", encoding="utf-8"):
                pass
            test_file.unlink(missing_ok=True)
            return candidate
        except OSError:
            continue

    return Path("/tmp")


LOG_DIR = _resolve_log_path()
LOG_FILE = LOG_DIR / "bot.log"


def get_logger(name: str = "discord_bot") -> logging.Logger:
    """Create a logger that writes to both the terminal and a daily rotating file."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_handler = TimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger