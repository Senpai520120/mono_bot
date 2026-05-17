import requests

def get_exchange_rate(target_currency):
    url = "https://api.monobank.ua/bank/currency"

    try:
        response = requests.get(url)
        data = response.json()

        currency_codes = {"USD": 840, "EUR": 978, "UAH": 980}
        target_id = currency_codes.get(target_currency)

        for item in data:
            if item.get('currencyCodeA') == target_id and item.get('currencyCodeB') == 980:
                return item.get('rateSell') or item.get('rateCross') or item.get('rateBuy')

    except:
        return None

    return None



