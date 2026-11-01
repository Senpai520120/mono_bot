import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VALID_CURRENCIES = ["USD", "EUR", "UAH"]

HISTORY_FILE = os.environ.get("HISTORY_FILE", os.path.join(BASE_DIR, "history.json"))
HISTORY_LIMIT = 10


def get_token():
    """Return the bot token from the TELEGRAM_BOT_TOKEN env variable, or None."""
    return os.environ.get("TELEGRAM_BOT_TOKEN", "").strip() or None
