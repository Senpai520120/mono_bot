# Технічне завдання на створення: Telegram бота для конвертації валют
# Загальна інформація
# Назва проєкту: Конвертер валют Telegram бот
# Мова програмування: Python
# Бібліотека для роботи з Telegram API: pyTelegramBotAPI
# API для отримання фінансових даних: https://api.monobank.ua/bank/currency проєкту
# Створити Telegram бота, який надає користувачам можливість конвертувати суму з однієї валюти до іншої, використовуючи фінансове API для отримання актуальних курсів валют.
# Функціонал
# Основні можливості бота:
# 1. Привітання та допомога:
# Бот вітає користувача при старті та надає інструкції щодо конвертації валют.
# 2. Конвертація валют:
# Користувач може ввести суму та обрати вихідну та цільову валюту для конвертації.
# Вихідна валюта задається за допомогою контексту (980 UAH)
# Цільова валюта здається за допомогою натискання клавіш.
# 3. Робота з файлами:
# Зберігати 10 останніх запитів на конвертацію у вигляді словника(у файлі JSON)
# Використані технології та бібліотеки
# Python 3.x
# pyTelegramBotAPI
# [Назва та версія бібліотеки для роботи з фінансовим API]

import telebot
import time

from config import VALID_CURRENCIES
from services.converter import convert_currency
from utils.history import save_history, get_history


class CurrencyBot:

    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.register_handlers()

    def register_handlers(self):
        self.bot.message_handler(commands=['start'])(self.start)
        self.bot.message_handler(commands=['history'])(self.history)
        self.bot.message_handler(content_types=['text'])(self.convert)
        self.bot.callback_query_handler(func=lambda call: True)(self.callback)

    def start(self, message):
        self.bot.send_message(
            message.chat.id,
            "Хай)\nВведи: 100 USD"
        )

    def convert(self, message):
        parts = message.text.split()

        if len(parts) != 2:
            self.bot.reply_to(message, "Формат: 100 USD")
            return

        try:
            amount = float(parts[0])
            currency_from = parts[1].upper()

            if currency_from not in VALID_CURRENCIES:
                self.bot.reply_to(message, "Тільки: USD, EUR, UAH")
                return

            markup = telebot.types.InlineKeyboardMarkup()

            for cur in VALID_CURRENCIES:
                if cur != currency_from:
                    btn = telebot.types.InlineKeyboardButton(
                        cur,
                        callback_data=f"{amount}_{currency_from}_{cur}"
                    )
                    markup.add(btn)

            self.bot.send_message(
                message.chat.id,
                f"Конвертувати {amount} {currency_from}:",
                reply_markup=markup
            )

        except:
            self.bot.reply_to(message, "Помилка")

    def callback(self, call):
        amount, from_currency, to_currency = call.data.split("_")
        amount = float(amount)

        result = convert_currency(amount, from_currency, to_currency)

        if result is None:
            self.bot.answer_callback_query(call.id, "Помилка API")
            return

        text = f"{amount} {from_currency} = {result} {to_currency}"

        save_history({
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "result": result,
            "time": time.ctime()
        })

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text
        )

    def history(self, message):
        history = get_history()

        if not history:
            self.bot.send_message(message.chat.id, "Історія порожня")
            return

        text = "Історія:\n\n"

        for entry in history:
            text += (
                f"{entry['time']}\n"
                f"{entry['amount']}"
                f" {entry['from']} = {entry['result']}"
                f" {entry['to']}\n\n"
            )

        self.bot.send_message(message.chat.id, text)

    def run(self):
        print("вроде работает ")
        self.bot.polling(none_stop=True)


