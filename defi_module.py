import random
import time
from web3 import Web3
from threading import Thread
from requests.adapters import Retry
import requests
from utils.mute_io_defi import MuteSwap
from utils.velocore_defi import Velocore
from utils.syncswap_defi import SynkSwap
from utils.space_fi_defi import SpaceFinance
from utils.symbiosis_defi import Symbosis
from utils.inch_defi import OneInch
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
        raise ValueError("\Wrong type for shuffle_wallets. Expected Boolean")
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

        token_list = [
            Web3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4')  # usdc
        ]

        log = logging.getLogger(threading.current_thread().name)
        console_out = logging.StreamHandler()
        basic_format1 = logging.Formatter('%(asctime)s : [%(name)s] : %(message)s')
        basic_format = logging.Formatter('%(asctime)s : %(message)s')
        console_out.setFormatter(basic_format1)
        file_handler = logging.FileHandler(f"DEFI {threading.current_thread().name}.txt", 'w', 'utf-8')
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

            arr_buy = []
            arr_sold = []
            swap_usdc = []

            if mute_swap is True:
                mute = MuteSwap(private_key, web3, str_number, log)
                arr_buy.append(mute)
                arr_sold.append(mute)
            if space_fi is True:
                space = SpaceFinance(private_key, web3, str_number, log)
                arr_buy.append(space)
                arr_sold.append(space)
                swap_usdc.append(space)
            if velocore is True:
                vel = Velocore(private_key, web3, str_number, log)
                arr_buy.append(vel)
                arr_sold.append(vel)
                swap_usdc.append(vel)
            if syncswap is True:
                synk = SynkSwap(private_key, web3, str_number, log)
                arr_buy.append(synk)
                arr_sold.append(synk)
                swap_usdc.append(synk)
            if symbiosis is True:
                symbios = Symbosis(private_key, web3, str_number, log)
                arr_buy.append(symbios)
                arr_sold.append(symbios)
            if one_inch is True:
                inch = OneInch(private_key, web3, str_number, log)
                arr_buy.append(inch)
                arr_sold.append(inch)
            len_way = len(arr_buy)
            random.shuffle(arr_buy)
            time.sleep(1)
            random.shuffle(arr_sold)
            time.sleep(1)
            random.shuffle(swap_usdc)

            if liquiditi_mute is True and mute_swap is True:
                liquidity_mute_index = random.randint(0, len_way - 2)

            if liquiditi_syncswap is True and syncswap is True:
                liquidity_sync_index = random.randint(0, len_way - 2)

            flag_liquiditi_mute = False
            flag_liquiditi_syncswap = False

            self.chek_gas_eth(max_gas, log)

            res = swap_usdc[0].sold_token(token_list[0])
            if res == 'balance':
                continue

            for i in range(number_of_repetitions):

                for j in range(len_way - 1):
                    rand = 0
                    value_swap = random.uniform(value_swap_min, value_swap_max)
                    self.chek_gas_eth(max_gas, log)
                    res = arr_buy[j].buy_token(token_list[rand], value_swap)
                    if res == 'balance':
                        break
                    time.sleep(random.randint(delay_between_tx_min, delay_between_tx_max))
                    self.chek_gas_eth(max_gas, log)
                    res = arr_sold[j].sold_token(token_list[rand])
                    if res == 'balance':
                        break
                    time.sleep(random.randint(delay_between_tx_min, delay_between_tx_max))

                    if liquiditi_mute is True and flag_liquiditi_mute is False:
                        if liquidity_mute_index == j:
                            value_liquid = random.uniform(liquidity_value_min, liquidity_value_max)
                            self.chek_gas_eth(max_gas, log)
                            res = mute.buy_token(token_list[0], value_liquid)
                            if res == 'balance':
                                break
                            time.sleep(random.randint(delay_between_tx_min, delay_between_tx_max))
                            self.chek_gas_eth(max_gas, log)
                            res = mute.add_liquidity(token_list[0])
                            if res == 'balance':
                                break
                            time.sleep(random.randint(delay_between_tx_min, delay_between_tx_max))
                            flag_liquiditi_mute = True

                    if liquiditi_syncswap is True and flag_liquiditi_syncswap is False:
                        if liquidity_sync_index == j:
                            value_liquid = random.uniform(liquidity_value_min, liquidity_value_max)
                            self.chek_gas_eth(max_gas, log)
                            res = synk.buy_token(token_list[0], value_liquid)
                            if res == 'balance':
                                break
                            time.sleep(random.randint(delay_between_tx_min, delay_between_tx_max))
                            self.chek_gas_eth(max_gas, log)
                            res = synk.add_liquidity(token_list[0])
                            if res == 'balance':
                                break
                            time.sleep(random.randint(delay_between_tx_min, delay_between_tx_max))
                            flag_liquiditi_syncswap = True

            if buy_usdc_at_the_end is True:
                res = swap_usdc[0].buy_token(token_list[0], 100)
                if res == 'balance':
                    continue

            session.close()


if __name__ == '__main__':
    with open("private_key.txt", "r") as f:
        list1 = [row.strip().split(' ') for row in f if row.strip()]
    keys_list = shuffle(list1, shuffle_wallets)
    all_wallets = len(keys_list)
    print(f'Wallets count: {all_wallets}\n')
    for _ in range(number_of_threads):
        worker = Worker()
        worker.start()
        time.sleep(10)
