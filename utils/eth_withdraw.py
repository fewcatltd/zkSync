# eth_withdraw.py

import random
from binance.client import Client
import logging

def setup_logging():
    logging.basicConfig(filename="BINANCE_LOG.txt", level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s", encoding='utf-8')
    
def generate_random_eth_amount(min_amount, max_amount, round_digits):
    random_amount = random.uniform(min_amount, max_amount)
    return round(random_amount, round_digits)

def withdraw_eth_to_address(api_key, secret_key, to_address, amount, network):
    setup_logging()
    client = Client(api_key, secret_key)

    try:
        response = client.withdraw(
            coin="ETH",
            address=to_address,
            amount=amount,
            network=network
        )

        if response["id"]:
            msg = f"Успешно отправлено {amount} ETH на адрес {to_address}."
            print(msg)
            logging.info(msg)
        else:
            msg = f"Ошибка при отправке ETH на адрес {to_address}. Причина: {response['msg']}"
            print(msg)
            logging.error(msg)
    except Exception as e:
        print(f"Ошибка при обработке адреса {to_address}. Причина: {str(e)}")
