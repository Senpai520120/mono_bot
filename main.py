import logging
import sys

from dotenv import load_dotenv

from config import get_token


def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    token = get_token()
    if not token:
        print(
            "Error: TELEGRAM_BOT_TOKEN is not set.\n"
            "Copy .env.example to .env and put your bot token from @BotFather there,\n"
            "or set the TELEGRAM_BOT_TOKEN environment variable.",
            file=sys.stderr,
        )
        return 1

    from bot import CurrencyBot

    CurrencyBot(token).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
