from web3 import Web3
import json as js
import random
from mimesis import Person
import time
from requests import ConnectionError
from utils.tg_bot import TgBot
from web3.exceptions import TransactionNotFound
from eth_utils import to_hex
from eth_abi import encode


class NameDomen(TgBot):
    def __init__(self, private_key, web3, number, log):
        self.private_key = private_key
        self.web3 = web3
        self.log = log
        self.number = number
        self.account = self.web3.eth.account.from_key(private_key)
        self.address_wallet = self.account.address
        self.address = Web3.to_checksum_address('0xAE23B6E7f91DDeBD3B70d74d20583E3e674Bd94f')
        self.abi = js.load(open('./abi/registerName.txt'))
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

    def mint_name(self, retry=0):
        try:
            name = ''
            person = Person('en')
            rand = random.randint(12345, 123456)
            name += person.first_name()
            name += person.last_name()
            name += str(rand)
            name = name.lower()
            self.log.info(f'Mint domen - {name}')
            len_name = Web3.to_hex(len(name))[2:]
            if len(len_name) < 2:
                len_name = '0' + len_name
            address_wal = to_hex(encode(['address'], [self.address_wallet]))[2:]
            payload = to_hex(encode(['bytes32'], [Web3.to_bytes(text=name)]))[2:]

            data = '0x9caf2b97' + '00000000000000000000000000000000000000000000000000000000000000e0' + address_wal + \
                   '0000000000000000000000000000000000000000000000000000000001e13380' + \
                   '0000000000000000000000000000000000000000000000000000000000000120' + \
                   '000000000000000000000000135a32c16765cef67dec3ae53b03f8c21feec0d8' +\
                   address_wal + '0000000000000000000000000000000000000000000000000000000000000000' \
                   + '00000000000000000000000000000000000000000000000000000000000000' + len_name +\
                   payload + '0000000000000000000000000000000000000000000000000000000000000002' + \
                   '7a6b000000000000000000000000000000000000000000000000000000000000'

            txn = {
                'chainId': 324,
                'data': data,
                'from': self.address_wallet,
                'to': self.address,
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                'gasPrice': self.web3.eth.gas_price,
                'gas': 100000,
                'value': Web3.to_wei(0.0027105, 'ether')
            }

            gas = self.web3.eth.estimate_gas(txn)
            txn.update({'gas': gas})

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(5)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')
            else:
                self.log.info('Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'Mint zkSync Name Service Domen', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.mint_name(retry)
                return
            hash_ = str(tx_hash.hex())
            self.log.info(f'[{self.number}] Mint zkSync Name Service Domen || https://explorer.zksync.io/tx/{hash_}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, 'Mint zkSync Name Service Domen', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Mint zkSync Name Service Domen', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.mint_name(retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Mint zkSync Name Service Domen', self.address_wallet,
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
                        TgBot.send_message_error(self, self.number, 'Mint zkSync Name Service Domen', self.address_wallet,
                                                 'insufficient funds')
                    return 0
            else:
                self.log.info(error)
                time.sleep(120)
                retry += 1
                if retry > 5:
                    return 0
                self.mint_name(retry)
