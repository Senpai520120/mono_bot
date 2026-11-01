from unittest.mock import Mock

import pytest
import requests

from services import api
from services.converter import convert_currency


def test_usd_to_uah(monobank_ok):
    assert convert_currency(100, "USD", "UAH") == 4585.05


def test_uah_to_usd(monobank_ok):
    assert convert_currency(4585.05, "UAH", "USD") == 100.0


def test_eur_to_usd_goes_through_uah(monobank_ok):
    assert convert_currency(10, "EUR", "USD") == round(10 * 51.2689 / 45.8505, 2)


def test_same_currency_needs_no_api(monobank_ok):
    assert convert_currency(12.345, "USD", "USD") == 12.35
    monobank_ok.assert_not_called()


def test_rates_are_cached(monobank_ok):
    convert_currency(1, "USD", "EUR")
    convert_currency(2, "EUR", "UAH")
    convert_currency(3, "UAH", "USD")
    assert monobank_ok.call_count == 1


def test_cache_expires(monobank_ok, monkeypatch):
    now = [1000.0]
    monkeypatch.setattr(api.time, "monotonic", lambda: now[0])
    convert_currency(1, "USD", "UAH")
    now[0] += api.CACHE_TTL + 1
    convert_currency(1, "USD", "UAH")
    assert monobank_ok.call_count == 2


def test_rate_limit_without_cache_returns_none(monkeypatch):
    response = Mock(status_code=429)
    response.raise_for_status.side_effect = requests.HTTPError("429 Too many requests")
    monkeypatch.setattr(api.requests, "get", Mock(return_value=response))
    assert convert_currency(100, "USD", "UAH") is None


def test_rate_limit_falls_back_to_stale_rates(monobank_ok, monkeypatch):
    now = [1000.0]
    monkeypatch.setattr(api.time, "monotonic", lambda: now[0])
    assert convert_currency(100, "USD", "UAH") == 4585.05

    now[0] += api.CACHE_TTL + 1
    monobank_ok.return_value.raise_for_status.side_effect = requests.HTTPError("429")
    assert convert_currency(100, "USD", "UAH") == 4585.05


def test_failed_request_is_not_retried_immediately(monkeypatch):
    get = Mock(side_effect=requests.ConnectionError("no network"))
    monkeypatch.setattr(api.requests, "get", get)
    assert convert_currency(1, "USD", "UAH") is None
    assert convert_currency(1, "USD", "UAH") is None
    assert get.call_count == 1


def test_unexpected_payload_returns_none(monkeypatch):
    response = Mock(status_code=200)
    response.json.side_effect = ValueError("not json")
    monkeypatch.setattr(api.requests, "get", Mock(return_value=response))
    assert convert_currency(1, "USD", "UAH") is None


@pytest.mark.parametrize("currency", ["GBP", "XYZ"])
def test_unknown_currency_returns_none(monobank_ok, currency):
    assert convert_currency(1, currency, "UAH") is None
