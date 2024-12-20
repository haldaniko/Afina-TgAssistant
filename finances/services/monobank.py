from dotenv import load_dotenv
import requests
import os

load_dotenv()

currencies = {
    "USD": {"flag": "🇺🇸", "symbol": "$", "code": 840},
    "EUR": {"flag": "🇪🇺", "symbol": "€", "code": 978},
    "PLN": {"flag": "🇵🇱", "symbol": "zł", "code": 985},
    "BGN": {"flag": "🇧🇬", "symbol": "лв", "code": 975},
    "UAH": {"flag": "🇺🇦", "symbol": "₴", "code": 980},
}

cryptocurrencies_list = ("BTC", "BCH", "ETH", "LTC")


class MonoBankAPI:
    def __init__(self, mono_token: str, iban_list: list[str]):
        self.mono_token = mono_token
        self.iban_list = iban_list

    def get_wallets(self):
        try:
            res = requests.get(
                "https://api.monobank.ua/personal/client-info",
                headers={'X-Token': self.mono_token}
            )
            data = res.json()
            result = {}
            for iban in self.iban_list:
                for account in data["accounts"]:
                    if account["iban"] == iban:
                        currency_code_value = account["currencyCode"]
                        currency_data = next(
                            (item for code, item in currencies.items() if item["code"] == currency_code_value), None)
                        if currency_data:
                            key = f"{account['type'].capitalize()} {currency_data['symbol']}"
                            result[key] = round(account['balance'] / 100, 2)
            return result
        except Exception as e:
            print("Exception (Monobank client info):", e)
            return None

    def set_webhook(self, webhook_url: str):
        try:
            data = requests.post(
                "https://api.monobank.ua/personal/webhook",
                headers={"X-Token": self.mono_token},
                json={"webHookUrl": webhook_url}
            )
            return data.status_code == 200
        except Exception as e:
            print("Exception (Monobank webhook):", e)
            return False

    def get_extract(self, account_id: str, from_timestamp: int):
        try:
            res = requests.get(
                f"https://api.monobank.ua/personal/statement/{account_id}/{from_timestamp}",
                headers={'X-Token': self.mono_token}
            )
            return res.json()
        except Exception as e:
            print("Exception (Monobank extract):", e)
            return None


class NBUAPI:
    @staticmethod
    def get_rates():
        try:
            rates = {}
            for currency_code in currencies.keys():
                res = requests.get(
                    "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange",
                    params={"valcode": currency_code, "json": ""}
                )
                data = res.json()
                if data:
                    rates[currency_code] = round(data[0]["rate"], 2)
            return rates
        except Exception as e:
            print("Exception (NBU rates):", e)
            return None


class CurrencyAPI:
    def __init__(self):
        self.apilayer_token = os.getenv("apilayerToken")
        self.coinlayer_token = os.getenv("coinlayerToken")

    def convert_currency(self, cur_to, cur_from, amount):
        try:
            res = requests.get(
                "https://api.apilayer.com/currency_data/convert",
                params={"to": cur_to, "from": cur_from, "amount": amount},
                headers={"apikey": self.apilayer_token}
            )
            data = res.json()
            return data["result"]
        except Exception as e:
            print("Exception (convert currency):", e)
            return None

    def get_cryptorates(self):
        try:
            res = requests.get(
                f"http://api.coinlayer.com/live?access_key={self.coinlayer_token}",
            )
            data = res.json()
            print(data)
            cryptocurrencies = {}
            for i in data["rates"]:
                if i in cryptocurrencies_list:
                    cryptocurrencies[i] = round(data["rates"][i], 2)
            return cryptocurrencies
        except Exception as e:
            print("Exception (coinlayer):", e)
            return None


if __name__ == "__main__":
    mono_token = os.getenv("monobankToken")
    iban_list = os.getenv("IBANs").split(",")
    bank_api = MonoBankAPI(mono_token=mono_token, iban_list=iban_list)
    print(bank_api.get_wallets())

