from web3 import Web3
import json as js
import time
from requests import ConnectionError
from utils.tg_bot import TgBot
from web3.exceptions import TransactionNotFound


class ZKsyncBridge(TgBot):
    def __init__(self, private_key, web3, number, max_gas, log):
        self.log = log
        self.private_key = private_key
        self.web3 = web3
        self.max_gas = max_gas
        self.number = number
        self.account = self.web3.eth.account.from_key(private_key)
        self.address_wallet = self.account.address
        self.address = Web3.to_checksum_address('0x32400084C286CF3E17e7B677ea9583e60a000324')
        self.abi = js.load(open('./abi/zkSync_bridge.txt'))
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

    def chek_gas_eth(self, max_gas):
        try:
            url_rpc = 'https://rpc.ankr.com/eth'
            eth_w3 = Web3(Web3.HTTPProvider(url_rpc, request_kwargs={'timeout': 600}))
            while True:
                res_ = int(round(Web3.from_wei(eth_w3.eth.gas_price, 'gwei')))
                if res_ <= max_gas:
                    break
                else:
                    self.log.info(f'Gas   is too high. Sleeping\n')
                    time.sleep(100)
                    continue
        except:
            return 0

    def bridge(self, value_eth, value_token, retry=0):
        value = Web3.to_wei(value_eth, 'ether')
        balance = self.web3.eth.get_balance(self.address_wallet)
        gas = 149210
        gas_price = self.web3.eth.gas_price
        l2_gas_limit = 762908
        l2_gas_per_pubdata_byte_limit = 800
        value_tok = Web3.to_wei(value_token, 'ether')
        comission_value = int(gas * gas_price * 1.1)
        self.chek_gas_eth(self.max_gas)

        if value > balance:
            value = balance - comission_value - value_tok
        else:
            if comission_value > balance - value:
                value = balance - comission_value - value_tok
        if value < Web3.to_wei(0.005, 'ether'):
            self.log.info('Bridge value less then 0.005 ETH')
            return 0
        self.log.info(f'Value bridge - {round(Web3.from_wei(value, "ether"), 5)} eth')
        try:
            contract_tx = self.contract.functions.requestL2Transaction(
                self.address_wallet,
                int(value * 0.95),
                b'',
                l2_gas_limit,
                l2_gas_per_pubdata_byte_limit,
                [],
                self.address_wallet
            ).build_transaction({
                'from': self.address_wallet,
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                'gasPrice': gas_price,
                'gas': gas,
                'value': value
            })
            signed_txn = self.web3.eth.account.sign_transaction(contract_tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(15)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')
            else:
                self.log.info('Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'Main Bridge', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.bridge(value_eth, value_token, retry)
                return
            hash_ = str(tx_hash.hex())
            self.log.info(f'Main bridge {round(Web3.from_wei(value, "ether"), 5)} eth complete\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Main bridge {round(Web3.from_wei(value, "ether"), 5)} eth', self.address_wallet,
                                           f'https://etherscan.io/tx/{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Main Bridge', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.bridge(value_eth, value_token, retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Main Bridge', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.bridge(value_eth, value_token, retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, 'Main Bridge', self.address_wallet,
                                                 'insufficient funds')
                    return 0
            else:
                self.log.info(error)
                time.sleep(120)
                retry += 1
                if retry > 5:
                    return 0
                self.bridge(value_eth, value_token, retry)
