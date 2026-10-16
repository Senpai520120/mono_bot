import os

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Set the TELEGRAM_BOT_TOKEN environment variable")

VALID_CURRENCIES = ["USD", "EUR", "UAH"]
