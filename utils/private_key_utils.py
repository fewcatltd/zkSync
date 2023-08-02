# private_key_utils.py

from eth_account import Account

def private_keys_to_addresses(private_keys):
    return [Account.from_key(private_key).address for private_key in private_keys]
