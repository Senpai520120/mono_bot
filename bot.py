"""Telegram bot that converts money between UAH, USD and EUR.

The user sends an amount and a source currency (e.g. "100 USD"), picks the
target currency with an inline button and gets the result calculated with
monobank's public exchange rates. The last 10 conversions are kept in a JSON file.
"""

import logging
import math
import time

import telebot
from telebot.apihelper import ApiTelegramException

from config import VALID_CURRENCIES
from services.converter import convert_currency
from utils.history import get_history, save_history

logger = logging.getLogger(__name__)

# Keeps callback_data well under Telegram's 64-byte limit.
MAX_AMOUNT = 1_000_000_000_000

START_TEXT = (
    "Hi! I convert money between UAH, USD and EUR using monobank exchange rates.\n\n"
    "Send an amount and a currency, for example: 100 USD\n"
    "Then pick the currency to convert to.\n\n"
    "/history - last 10 conversions"
)
FORMAT_HINT = "Send an amount and a currency, for example: 100 USD"
RATES_UNAVAILABLE = "Exchange rates are temporarily unavailable. Please try again in a minute."


def parse_request(text):
    """Parse "100 usd" into (100.0, "USD").

    Raises ValueError with a message that can be shown to the user.
    """
    parts = (text or "").split()
    if len(parts) != 2:
        raise ValueError(FORMAT_HINT)

    raw_amount, currency = parts[0].replace(",", "."), parts[1].upper()
    try:
        amount = float(raw_amount)
    except ValueError:
        raise ValueError(f'"{parts[0]}" is not a number. {FORMAT_HINT}') from None

    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("The amount must be a positive number.")
    if amount > MAX_AMOUNT:
        raise ValueError("The amount is too large.")
    if currency not in VALID_CURRENCIES:
        raise ValueError(f"Supported currencies: {', '.join(VALID_CURRENCIES)}")
    return amount, currency


def format_amount(value):
    return f"{value:.2f}"


class CurrencyBot:

    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.register_handlers()

    def register_handlers(self):
        self.bot.message_handler(commands=['start', 'help'])(self.start)
        self.bot.message_handler(commands=['history'])(self.history)
        self.bot.message_handler(content_types=['text'])(self.convert)
        self.bot.callback_query_handler(func=lambda call: True)(self.callback)

    def start(self, message):
        self.bot.send_message(message.chat.id, START_TEXT)

    def convert(self, message):
        try:
            amount, currency_from = parse_request(message.text)
        except ValueError as exc:
            self.bot.reply_to(message, str(exc))
            return

        markup = telebot.types.InlineKeyboardMarkup()
        for cur in VALID_CURRENCIES:
            if cur != currency_from:
                markup.add(telebot.types.InlineKeyboardButton(
                    cur,
                    callback_data=f"{amount}_{currency_from}_{cur}",
                ))

        self.bot.send_message(
            message.chat.id,
            f"Convert {format_amount(amount)} {currency_from} to:",
            reply_markup=markup,
        )

    def callback(self, call):
        try:
            raw_amount, from_currency, to_currency = call.data.split("_")
            amount = float(raw_amount)
        except (AttributeError, ValueError):
            self.bot.answer_callback_query(call.id, "Unknown button, please send a new request.")
            return

        result = convert_currency(amount, from_currency, to_currency)
        if result is None:
            self.bot.answer_callback_query(call.id, RATES_UNAVAILABLE, show_alert=True)
            return

        self.bot.answer_callback_query(call.id)
        text = f"{format_amount(amount)} {from_currency} = {format_amount(result)} {to_currency}"

        try:
            save_history({
                "amount": amount,
                "from": from_currency,
                "to": to_currency,
                "result": result,
                "time": time.ctime(),
            })
        except OSError:
            logger.exception("Could not save conversion history")

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
        )

    def history(self, message):
        history = get_history()

        if not history:
            self.bot.send_message(message.chat.id, "No conversions yet.")
            return

        text = "Last conversions:\n\n"
        for entry in history:
            text += (
                f"{entry['time']}\n"
                f"{format_amount(entry['amount'])} {entry['from']}"
                f" = {format_amount(entry['result'])} {entry['to']}\n\n"
            )

        self.bot.send_message(message.chat.id, text)

    def run(self):
        try:
            me = self.bot.get_me()
        except ApiTelegramException as exc:
            raise SystemExit(f"Error: Telegram rejected the bot token ({exc.description}). "
                             "Check TELEGRAM_BOT_TOKEN.") from None
        logger.info("Bot @%s is running. Press Ctrl+C to stop.", me.username)
        self.bot.infinity_polling()
