from services.api import get_exchange_rate


def convert_currency(amount, from_currency, to_currency):
    """Convert amount via UAH. Returns the rounded result, or None if rates are unavailable."""
    if from_currency == to_currency:
        return round(amount, 2)

    rate_from = get_exchange_rate(from_currency)
    rate_to = get_exchange_rate(to_currency)
    if rate_from is None or rate_to is None:
        return None

    amount_in_uah = amount * rate_from
    return round(amount_in_uah / rate_to, 2)
