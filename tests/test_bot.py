from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import bot as bot_module
from bot import CurrencyBot, parse_request


@pytest.mark.parametrize("text, expected", [
    ("100 USD", (100.0, "USD")),
    ("12.5 eur", (12.5, "EUR")),
    ("12,5 uah", (12.5, "UAH")),
    ("  7   usd ", (7.0, "USD")),
])
def test_parse_request_valid(text, expected):
    assert parse_request(text) == expected


@pytest.mark.parametrize("text, message_part", [
    ("100", "for example"),
    ("100 USD EUR", "for example"),
    ("", "for example"),
    ("abc USD", "is not a number"),
    ("nan USD", "positive"),
    ("inf USD", "positive"),
    ("-5 USD", "positive"),
    ("0 USD", "positive"),
    ("1e20 USD", "too large"),
    ("100 GBP", "Supported currencies"),
])
def test_parse_request_invalid(text, message_part):
    with pytest.raises(ValueError, match=message_part):
        parse_request(text)


@pytest.fixture
def currency_bot():
    b = CurrencyBot("123456:TEST")
    b.bot = Mock()
    return b


def make_call(data):
    return SimpleNamespace(
        id="cb1",
        data=data,
        message=SimpleNamespace(chat=SimpleNamespace(id=42), message_id=7),
    )


def test_callback_converts_and_saves_history(currency_bot, monkeypatch):
    monkeypatch.setattr(bot_module, "convert_currency", lambda a, f, t: 4585.05)
    saved = []
    monkeypatch.setattr(bot_module, "save_history", saved.append)

    currency_bot.callback(make_call("100.0_USD_UAH"))

    currency_bot.bot.edit_message_text.assert_called_once_with(
        chat_id=42, message_id=7, text="100.00 USD = 4585.05 UAH")
    assert saved[0]["result"] == 4585.05


def test_callback_reports_unavailable_rates(currency_bot, monkeypatch):
    monkeypatch.setattr(bot_module, "convert_currency", lambda a, f, t: None)
    currency_bot.callback(make_call("100.0_USD_UAH"))
    currency_bot.bot.answer_callback_query.assert_called_once()
    assert "temporarily unavailable" in currency_bot.bot.answer_callback_query.call_args.args[1]
    currency_bot.bot.edit_message_text.assert_not_called()


def test_callback_ignores_garbage_data(currency_bot):
    currency_bot.callback(make_call("garbage"))
    currency_bot.bot.edit_message_text.assert_not_called()


def test_convert_replies_with_error_for_bad_input(currency_bot):
    message = SimpleNamespace(text="abc USD", chat=SimpleNamespace(id=1))
    currency_bot.convert(message)
    assert "is not a number" in currency_bot.bot.reply_to.call_args.args[1]
