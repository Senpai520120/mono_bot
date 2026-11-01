import logging
import threading
import time

import requests

MONOBANK_URL = "https://api.monobank.ua/bank/currency"

# monobank refreshes public rates at most every 5 minutes and answers
# "429 Too many requests" if the endpoint is called more often than about once a minute.
CACHE_TTL = 300
RETRY_AFTER = 60
REQUEST_TIMEOUT = 10

CURRENCY_CODES = {"USD": 840, "EUR": 978, "UAH": 980}
UAH_CODE = 980

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_cache = {"rates": None, "fetched_at": None, "last_attempt": None}


def _fetch_rates():
    """Download rates from monobank: {ISO 4217 numeric code: price in UAH}."""
    response = requests.get(MONOBANK_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    rates = {}
    for item in response.json():
        if item.get("currencyCodeB") != UAH_CODE:
            continue
        rate = item.get("rateSell") or item.get("rateCross") or item.get("rateBuy")
        if rate:
            rates[item.get("currencyCodeA")] = rate
    return rates


def get_rates():
    """Return cached rates, refreshing them when the cache is older than CACHE_TTL.

    On a network error or a 429 the last known rates are returned (or None if
    there are none yet), and monobank is not asked again for RETRY_AFTER seconds.
    """
    with _lock:
        now = time.monotonic()
        fetched_at = _cache["fetched_at"]
        last_attempt = _cache["last_attempt"]

        if fetched_at is not None and now - fetched_at < CACHE_TTL:
            return _cache["rates"]
        if last_attempt is not None and now - last_attempt < RETRY_AFTER:
            return _cache["rates"]

        _cache["last_attempt"] = now
        try:
            _cache["rates"] = _fetch_rates()
            _cache["fetched_at"] = now
        except (requests.RequestException, ValueError, TypeError, AttributeError) as exc:
            logger.warning("Could not fetch monobank rates: %s", exc)
        return _cache["rates"]


def get_exchange_rate(target_currency):
    """Price of one unit of target_currency in UAH, or None if unknown/unavailable."""
    if target_currency == "UAH":
        return 1.0

    code = CURRENCY_CODES.get(target_currency)
    if code is None:
        return None

    rates = get_rates()
    if not rates:
        return None
    return rates.get(code)


def clear_cache():
    """Forget cached rates (used by tests)."""
    with _lock:
        _cache.update(rates=None, fetched_at=None, last_attempt=None)
