# mono_bot

[![CI](https://github.com/Senpai520120/mono_bot/actions/workflows/ci.yml/badge.svg)](https://github.com/Senpai520120/mono_bot/actions/workflows/ci.yml)

A Telegram bot that converts money between **UAH, USD and EUR** using the public
exchange rates of [monobank](https://api.monobank.ua/docs/).

## Features

- `/start` (or `/help`) explains how to use the bot.
- Send an amount and a currency, e.g. `100 USD` (`12,5 eur` also works). The bot
  replies with buttons for the target currency and returns the converted amount.
- `/history` shows the last 10 conversions, stored in `history.json`.
- Rates are cached for 5 minutes. monobank refreshes them no more often than that
  and answers `429 Too many requests` when the endpoint is called too often. If
  monobank is unreachable, the bot uses the last known rates or tells the user to
  try again in a minute.
- Invalid input (`abc USD`, `-5 USD`, `100 GBP`) gets a clear reply instead of a
  generic error.

## Example dialog

```
You:  /start
Bot:  Hi! I convert money between UAH, USD and EUR using monobank exchange rates.
      Send an amount and a currency, for example: 100 USD
You:  100 USD
Bot:  Convert 100.00 USD to:   [EUR] [UAH]
You:  *taps UAH*
Bot:  100.00 USD = 4585.05 UAH
You:  /history
Bot:  Last conversions:
      Sun Nov  1 12:00:00 2026
      100.00 USD = 4585.05 UAH
```

## Quick start

Requires Python 3.10+ and a bot token from [@BotFather](https://t.me/BotFather).

```bash
git clone https://github.com/Senpai520120/mono_bot.git
cd mono_bot
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # Windows PowerShell: Copy-Item .env.example .env
# open .env and set TELEGRAM_BOT_TOKEN=...
python main.py
```

The token is read from the `TELEGRAM_BOT_TOKEN` environment variable (or from
`.env`). It is never stored in the code. If the token is missing or rejected by
Telegram, the bot exits with a clear message.

## Tests

The monobank API is mocked, so the tests need no network and no token.

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```

## Project structure

```
main.py                 entry point: loads .env, checks the token, starts the bot
bot.py                  Telegram handlers and input parsing
config.py               supported currencies and settings
services/api.py         monobank client with a 5-minute cache
services/converter.py   conversion through UAH
utils/history.py        last 10 conversions in a JSON file (thread-safe, atomic writes)
tests/                  pytest tests
```

## Stack

Python, pyTelegramBotAPI, requests, python-dotenv, pytest, ruff, GitHub Actions.
