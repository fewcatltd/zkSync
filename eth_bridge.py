import time
from Constants import *
from threading import Thread
import threading
from requests.adapters import Retry
import requests
import random
from web3 import Web3
from utils.official_zkSync_Era import ZKsyncBridge
import logging


def shuffle(wallets_list, shuffle_wallets):
    if shuffle_wallets is True:
        random.shuffle(wallets_list)
        numbered_wallets = list(enumerate(wallets_list, start=1))
    elif shuffle_wallets is False:
        numbered_wallets = list(enumerate(wallets_list, start=1))
    else:
        raise ValueError("\n\nWrong type for shuffle_wallets. Expected Boolean")
    return numbered_wallets


class Worker(Thread):
    def __int__(self):
        super().__init__()

    def run(self):
        
        log = logging.getLogger(threading.current_thread().name)
        console_out = logging.StreamHandler()
        basic_format1 = logging.Formatter('%(asctime)s : [%(name)s] : %(message)s')
        basic_format = logging.Formatter('%(asctime)s : %(message)s')
        console_out.setFormatter(basic_format1)
        file_handler = logging.FileHandler(f"zkSync bridge {threading.current_thread().name}.txt", 'w', 'utf-8')
        file_handler.setFormatter(basic_format)
        log.setLevel(logging.DEBUG)
        log.addHandler(console_out)
        log.addHandler(file_handler)
        
        while keys_list:
            account = keys_list.pop(0)
            number = account[0]
            private_key = account[1][0]
            rpc = RPC_ETH
            retries = Retry(total=10, backoff_factor=1, status_forcelist=[400, 404, 500, 502, 503, 504])
            adapter = requests.adapters.HTTPAdapter(max_retries=retries)
            session = requests.Session()
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            web3 = Web3(
                Web3.HTTPProvider(rpc, request_kwargs={'timeout': 600}, session=session))

            str_number = f'{number} / {all_wallets}'
            address = web3.eth.account.from_key(private_key).address
            log.info(f'Start cycle for {address}\n\n')
            bridge = ZKsyncBridge(private_key, web3, str_number, max_gas, log)
            value = random.uniform(value_bridge_eth_min, value_bridge_eth_max)
            bridge.bridge(value, min_token)
            time.sleep(random.randint(delay_between_tx_min, delay_between_tx_max))
            session.close()


if __name__ == '__main__':
    with open("private_key.txt", "r") as f:
        list1 = [row.strip().split('%') for row in f if row.strip()]
    keys_list = shuffle(list1, shuffle_wallets)
    all_wallets = len(keys_list)
    print(f'Number of wallets: {all_wallets}\n')
    for _ in range(number_of_threads):
        worker = Worker()
        worker.start()
        time.sleep(10)
