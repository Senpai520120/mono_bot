from services.api import get_exchange_rate

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount

    rates = {
        "USD": get_exchange_rate("USD"),
        "EUR": get_exchange_rate("EUR"),
        "UAH": 1
    }

    if None in rates.values():
        return None

    amount_in_uah = amount * rates[from_currency]
    result = amount_in_uah / rates[to_currency]

    return round(result, 2)




