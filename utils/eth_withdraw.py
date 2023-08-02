# eth_withdraw.py

import random
from binance.client import Client

def generate_random_eth_amount(min_amount, max_amount, round_digits):
    random_amount = random.uniform(min_amount, max_amount)
    return round(random_amount, round_digits)

def withdraw_eth_to_address(api_key, secret_key, to_address, amount, network):
    client = Client(api_key, secret_key)

    try:
        response = client.withdraw(
            coin="ETH",
            address=to_address,
            amount=amount,
            network=network
        )

        if response["id"]:
            print(f"Успешно отправлено {amount} ETH на адрес {to_address}.")
        else:
            print(f"Ошибка при отправке ETH на адрес {to_address}. Причина: {response['msg']}")
    except Exception as e:
        print(f"Ошибка при обработке адреса {to_address}. Причина: {str(e)}")
