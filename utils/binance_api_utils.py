# binance_api_utils.py

from dotenv import dotenv_values

def get_binance_api_keys():
    config = dotenv_values(".env")
    return config["BINANCE_API_KEY"], config["BINANCE_SECRET_KEY"]
