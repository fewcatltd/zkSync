import random
import time
from web3 import Web3
from threading import Thread
from requests.adapters import Retry
import requests
from utils.send_money import SendYourself
from Constants import *
import logging
import threading


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

    def chek_gas_eth(self, max_gas_, log):
        try:
            eth_w3 = Web3(Web3.HTTPProvider(RPC_ETH, request_kwargs={'timeout': 600}))
            while True:
                res = int(round(Web3.from_wei(eth_w3.eth.gas_price, 'gwei')))
                if res <= max_gas_:
                    break
                else:
                    log.info(f'Gas   is too high. Sleeping\n')
                    time.sleep(100)
                    continue
        except:
            return 0

    def run(self):

        log = logging.getLogger(threading.current_thread().name)
        console_out = logging.StreamHandler()
        basic_format1 = logging.Formatter('%(asctime)s : [%(name)s] : %(message)s')
        basic_format = logging.Formatter('%(asctime)s : %(message)s')
        console_out.setFormatter(basic_format1)
        file_handler = logging.FileHandler(f"Self mixer {threading.current_thread().name}.txt", 'w', 'utf-8')
        file_handler.setFormatter(basic_format)
        log.setLevel(logging.DEBUG)
        log.addHandler(console_out)
        log.addHandler(file_handler)

        while keys_list:
            account = keys_list.pop(0)
            number = account[0]
            private_key = account[1][0]
            rpc = RPC_ZKSYNK
            retries = Retry(total=10, backoff_factor=1, status_forcelist=[400, 404, 500, 502, 503, 504])
            adapter = requests.adapters.HTTPAdapter(max_retries=retries)
            session = requests.Session()
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            web3 = Web3(
                Web3.HTTPProvider(rpc, request_kwargs={'timeout': 600}, session=session))

            address = web3.eth.account.from_key(private_key).address
            log.info(f'Start cycle for {address}\n\n')

            str_number = f'{number} / {all_wallets}'

            number_repetitions = random.randint(number_transactions_min, number_transactions_max)
            im = SendYourself(private_key, web3, str_number, log)
            for _ in range(number_repetitions):
                self.chek_gas_eth(max_gas, log)
                value_send = round(random.uniform(value_send_min, value_send_max), decimals_send)
                im.send(value_send)
                time.sleep(random.randint(delay_between_tx_min, delay_between_tx_max))
            session.close()


if __name__ == '__main__':
    with open("private_key.txt", "r") as f:
        list1 = [row.strip().split(' ') for row in f if row.strip()]
    keys_list = shuffle(list1, shuffle_wallets)
    all_wallets = len(keys_list)
    print(f'Number of wallets: {all_wallets}\n')
    for _ in range(number_of_threads):
        worker = Worker()
        worker.start()
        time.sleep(10)
