import random
import requests
from urllib.parse import urlencode
import hmac
import hashlib
import time
import logging
from dotenv import dotenv_values

def setup_logging():
    logging.basicConfig(filename="BINANCE_LOG.txt", level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

def read_private_keys_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def get_binance_api_keys():
    config = dotenv_values(".env")
    return config["BINANCE_API_KEY"], config["BINANCE_SECRET_KEY"]

def generate_random_eth_amount(min_amount, max_amount, round_digits):
    random_amount = random.uniform(min_amount, max_amount)
    return round(random_amount, round_digits)

def withdraw_eth_to_address(api_key, secret_key, to_address, amount, network):
    endpoint = "https://api.binance.com/sapi/v1/capital/withdraw/apply"
    params = {
        "coin": "ETH",
        "withdrawOrderId": int(time.time() * 1000),
        "network": network,
        "address": to_address,
        "amount": amount,
        "timestamp": int(time.time() * 1000)
    }
    query_string = urlencode(params)
    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params["signature"] = signature

    headers = {"X-MBX-APIKEY": api_key}
    response = requests.post(endpoint, params=params, headers=headers)
    response_data = response.json()

    if response_data["success"]:
        msg = f"Успешно отправлено {amount} ETH на адрес {to_address}."
        print(msg)
        logging.info(msg)
    else:
        msg = f"Ошибка при отправке ETH на адрес {to_address}. Причина: {response_data['msg']}"
        print(msg)
        logging.error(msg)

def get_float_input(prompt):
    while True:
        try:
            value = input(prompt).replace(',', '.')
            return float(value)
        except ValueError:
            print("Некорректный ввод. Пожалуйста, введите число.")

if __name__ == "__main__":
    setup_logging()

    private_keys_file = "private_key.txt"
    private_keys = read_private_keys_from_file(private_keys_file)

    num_addresses = int(input("Сколько адресов для вывода эфира? "))

    same_amount = input("Вывести на все адреса одинаковое количество эфира? (да/нет): ").lower() == "да"

    if same_amount:
        eth_amount = get_float_input("Укажите количество эфира для всех адресов: ")
    else:
        min_amount = get_float_input("Укажите минимальное количество эфира для вывода: ")
        max_amount = get_float_input("Укажите максимальное количество эфира для вывода: ")
        round_digits = int(input("До скольки знаков после запятой округлять количество эфира: "))

    network = input("Выберите сеть для отправки ETH (1 - ARBITRUM, 2 - OPTIMISM): ")
    if network == "1":
        network = "ARBITRUM"
    elif network == "2":
        network = "OPTIMISM"
    else:
        print("Некорректный выбор сети. Пожалуйста, выберите 1 или 2.")
        exit(1)

    binance_api_key, binance_secret_key = get_binance_api_keys()

    for address in private_keys[:num_addresses]:
        if same_amount:
            eth_amount = eth_amount
        else:
            eth_amount = generate_random_eth_amount(min_amount, max_amount, round_digits)

        try:
            withdraw_eth_to_address(binance_api_key, binance_secret_key, address, eth_amount, network)
        except Exception as e:
            msg = f"Ошибка при обработке адреса {address}. Причина: {str(e)}"
            print(msg)
            logging.error(msg)
