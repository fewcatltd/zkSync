import random

from web3 import Web3
import json as js
import time
from requests import ConnectionError
from web3.exceptions import TransactionNotFound
from utils.tg_bot import TgBot


class SendMessage(TgBot):

    def __init__(self, private_key, web3, number, log):
        self.private_key = private_key
        self.web3 = web3
        self.number = number
        self.log = log
        self.account = self.web3.eth.account.from_key(private_key)
        self.address_wallet = self.account.address
        self.address_arb_nova = Web3.to_checksum_address('0xeEf87D3A99405C78D65F27330DC31Bd6A1796aEA')
        self.address_arb = Web3.to_checksum_address('0xEb762C289c1A3BdF2375679c1c69b745F9CDc17f')
        self.address_meter = Web3.to_checksum_address('0x5467c948300CE2F3Eb84EE5f05226633EaE12B49')
        self.address_fantom = Web3.to_checksum_address('0xde9C0EA47b3cA1f84a9Dc78Ddb0994Da179d67e4')
        self.abi = js.load(open('./abi/sendMessage.txt'))
        self.contract = self.web3.eth.contract(address=self.address_arb_nova, abi=self.abi)
        self.contract_meter = self.web3.eth.contract(address=self.address_meter, abi=self.abi)
        self.contract_fantom = self.web3.eth.contract(address=self.address_fantom, abi=self.abi)
        self.contract_arb = self.web3.eth.contract(address=self.address_arb, abi=self.abi)

    def send(self, chain_id, retry=0):
        self.log.info(f'Send message chain_id#{chain_id}')
        with open('utils/words.txt', 'r') as f:
            list_word = f.readlines()
        word = random.choice(list_word)[:-1]
        if chain_id == 110:
            value = Web3.to_wei(0.00065, 'ether')
            text = 'Arbitrum'
            contract = self.contract_arb
        elif chain_id == 175:
            value = Web3.to_wei(0.00027, 'ether')
            text = 'Arbitrum Nova'
            contract = self.contract
        elif chain_id == 176:
            value = Web3.to_wei(0.00034, 'ether')
            text = 'Meter'
            contract = self.contract_meter
        elif chain_id == 158:
            value = Web3.to_wei(0.0012, 'ether')
            text = 'Polygon ZK EVM'
            contract = self.contract
        else:
            value = Web3.to_wei(0.0006, 'ether')
            text = 'Fantom'
            contract = self.contract_fantom
        try:
            contract_txn = contract.functions.sendMessage(word, chain_id).build_transaction(
            {
                'from': self.address_wallet,
                'value': value,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            })
            signed_txn = self.web3.eth.account.sign_transaction(contract_txn, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(5)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')
            else:
                self.log.info('Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'Buy token MuteSwap', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.send(chain_id, retry)
                return

            hash_ = str(tx_hash.hex())
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Send message "{word}" to {text}', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
            self.log.info(f'[{self.number}] Send message "{word}" to {text} || https://explorer.zksync.io/tx/{hash_}\n')

        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, f'Send message "{word}" to {text}', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.send(chain_id, retry)

        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, f'Send message "{word}" to {text}', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.send(chain_id, retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient balance' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, f'Send message "{word}" to {text}', self.address_wallet,
                                                 'insufficient funds')
                    return 'balance'
            else:
                self.log.info(error)
                time.sleep(120)
                retry += 1
                if retry > 5:
                    return 0
                self.send(chain_id, retry)
