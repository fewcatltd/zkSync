# main.py

import logging
from utils.float_input_utils import get_float_input
from utils.binance_api_utils import get_binance_api_keys
from utils.private_key_utils import private_keys_to_addresses
from utils.eth_withdraw import generate_random_eth_amount, withdraw_eth_to_address

def setup_logging():
    logging.basicConfig(filename="BINANCE_LOG.txt", level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s", encoding='utf-8')

def read_private_keys_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

if __name__ == "__main__":
    setup_logging()

    private_keys_file = "private_key.txt"
    private_keys = read_private_keys_from_file(private_keys_file)

    num_addresses = int(input("Сколько адресов для вывода эфира? "))

    # Преобразуем приватные ключи в адреса
    addresses = private_keys_to_addresses(private_keys)

    same_amount_choice = input("Вывести на все адреса одинаковое количество эфира? (1 - да, 2 - нет): ")

    if same_amount_choice == "1":
        same_amount = True
        eth_amount = get_float_input("Укажите количество эфира для всех адресов: ")
    elif same_amount_choice == "2":
        same_amount = False
        min_amount = get_float_input("Укажите минимальное количество эфира для вывода: ")
        max_amount = get_float_input("Укажите максимальное количество эфира для вывода: ")
        round_digits = int(input("До скольки знаков после запятой округлять количество эфира: "))
    else:
        print("Некорректный выбор. Пожалуйста, выберите 1 или 2.")
        exit(1)

    network_choice = input("Выберите сеть для отправки ETH (1 - ARBITRUM, 2 - OPTIMISM): ")
    if network_choice == "1":
        network = "arbitrum"
    elif network_choice == "2":
        network = "optimism"
    else:
        print("Некорректный выбор сети. Пожалуйста, выберите 1 или 2.")
        exit(1)

    binance_api_key, binance_secret_key = get_binance_api_keys()

    for address in addresses[:num_addresses]:
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
