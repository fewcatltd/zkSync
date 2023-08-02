import time
from Constants import *
from threading import Thread
import threading
from requests.adapters import Retry
import requests
import random
from web3 import Web3
from utils.orbiter_finance_bridge import Orbiter
import logging


zksynk = {
    'name': 'zksync',
    'scan': 'https://explorer.zksync.io/tx/'
}

arbitrum = {
    'name': 'arbitrum',
    'scan': 'https://arbiscan.io/tx/'
}

optimism = {
    'name': 'optimism',
    'scan': 'https://optimistic.etherscan.io/'
}


def gat_chain(chain_fr, chain_t):
    if chain_fr == 'Arbitrum':
        chain1 = arbitrum
    elif chain_fr == 'ZkSync':
        chain1 = zksynk
    elif chain_fr == 'Optimism':
        chain1 = optimism
    else:
        raise ValueError("\nWrong 'chain_from'. Expected 'Arbitrum' or 'ZkSync' or 'Optimism'.")

    if chain_t == 'Arbitrum':
        chain2 = arbitrum
    elif chain_t == 'ZkSync':
        chain2 = zksynk
    elif chain_t == 'Optimism':
        chain2 = optimism
    else:
        raise ValueError("\nWrong 'chain_to'. Expected 'Arbitrum' or 'ZkSync' or 'Optimism'.")

    return chain1, chain2


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
        file_handler = logging.FileHandler(f"Orbiter {threading.current_thread().name}.txt", 'w', 'utf-8')
        file_handler.setFormatter(basic_format)
        log.setLevel(logging.DEBUG)
        log.addHandler(console_out)
        log.addHandler(file_handler)

        while keys_list:
            account = keys_list.pop(0)
            number = account[0]
            private_key = account[1][0]
            if chain_from == zksynk:
                rpc = RPC_ZKSYNK
                scan = 'https://explorer.zksync.io/tx/'
            elif chain_from == arbitrum:
                rpc = RPC_ARBITRUM
                scan = 'https://arbiscan.io/tx/'
            else:
                rpc = RPC_OPTIMISM
                scan = 'https://optimistic.etherscan.io/tx/'
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
            bridge = Orbiter(private_key, web3, str_number, log, scan)
            value = random.uniform(orbiter_bridge_eth_min, orbiter_bridge_eth_max)
            bridge.bridge(value, chain_to)
            time.sleep(random.randint(delay_between_tx_min, delay_between_tx_max))
            session.close()


if __name__ == '__main__':
    with open("private_key.txt", "r") as f:
        list1 = [row.strip().split('%') for row in f if row.strip()]
    keys_list = shuffle(list1, shuffle_wallets)
    chain_from, chain_to = gat_chain(CHAIN_FROM, CHAIN_TO)
    all_wallets = len(keys_list)
    print(f'Number of wallets: {all_wallets}\n')
    for _ in range(number_of_threads):
        worker = Worker()
        worker.start()
        time.sleep(10)
