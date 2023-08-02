from web3 import Web3
import json as js
import random
from mimesis import Person
import time
from requests import ConnectionError
from utils.tg_bot import TgBot
from web3.exceptions import TransactionNotFound


class Holograph(TgBot):
    def __init__(self, private_key, web3, number, log):
        self.private_key = private_key
        self.web3 = web3
        self.log = log
        self.number = number
        self.account = self.web3.eth.account.from_key(private_key)
        self.address_wallet = self.account.address
        self.address = Web3.to_checksum_address('0x61b2d56645d697ac3a27c2fa1e5b26b45429d1a9')
        self.abi = js.load(open('./abi/holograph.txt'))
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

    def mint(self, retry=0):
        try:
            self.log.info(f'Mint Holograph nft')
            contract_tx = self.contract.functions.purchase(1).build_transaction({
                'from': self.address_wallet,
                'value': 0,
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                'gasPrice': self.web3.eth.gas_price
            })

            signed_txn = self.web3.eth.account.sign_transaction(contract_tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.log.info(f'Transaction sent: https://optimistic.etherscan.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(5)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')
            else:
                self.log.info('Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'Mint NFT Domen', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.mint_name(retry)
                return
            hash_ = str(tx_hash.hex())
            self.log.info(f'[{self.number}] Mint NFT Domen || https://optimistic.etherscan.io/tx/{hash_}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, 'Mint NFT Domen', self.address_wallet,
                                           f'https://optimistic.etherscan.io/tx/{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Mint NFT Domen', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.mint_name(retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Mint NFT Domen', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.mint_name(retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, 'Mint NFT Domen', self.address_wallet,
                                                 'insufficient funds')
                    return 0
            self.log.info(error)