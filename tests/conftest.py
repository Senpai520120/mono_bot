import os
import sys
from unittest.mock import Mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import api  # noqa: E402

# Trimmed real response from https://api.monobank.ua/bank/currency
MONOBANK_SAMPLE = [
    {"currencyCodeA": 840, "currencyCodeB": 980, "date": 1793484073, "rateBuy": 45.45, "rateSell": 45.8505},
    {"currencyCodeA": 978, "currencyCodeB": 980, "date": 1793484073, "rateBuy": 50.57, "rateSell": 51.2689},
    {"currencyCodeA": 978, "currencyCodeB": 840, "date": 1793484073, "rateBuy": 1.112, "rateSell": 1.122},
    {"currencyCodeA": 826, "currencyCodeB": 980, "date": 1793557184, "rateCross": 61.6087},
]


@pytest.fixture(autouse=True)
def fresh_cache():
    api.clear_cache()
    yield
    api.clear_cache()


@pytest.fixture
def monobank_ok(monkeypatch):
    response = Mock(status_code=200)
    response.json.return_value = MONOBANK_SAMPLE
    response.raise_for_status.return_value = None
    get = Mock(return_value=response)
    monkeypatch.setattr(api.requests, "get", get)
    return get
