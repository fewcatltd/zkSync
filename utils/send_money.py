from web3 import Web3
import time
from requests import ConnectionError
from utils.tg_bot import TgBot
from web3.exceptions import TransactionNotFound


class SendYourself(TgBot):

    def __init__(self, private_key, web3, number, log):
        self.web3 = web3
        self.log = log
        self.number = number
        self.private_key = private_key
        self.address_wallet = self.web3.eth.account.from_key(private_key).address

    def send(self, amount_eth, retry=0):
        balance = self.web3.eth.get_balance(self.address_wallet)
        value = Web3.to_wei(amount_eth, 'ether')
        if value > balance:
            value = balance - Web3.to_wei(0.003, 'ether')
            if value < Web3.to_wei(0.000001, 'ether'):
                self.log.info('Insufficient funds')
                return 'balance'
        val = round(Web3.from_wei(value, 'ether'), 10)
        self.log.info(f'Send {val} ETH')
        try:
            txn = {
                'chainId': 324,
                'from': self.address_wallet,
                'to': self.address_wallet,
                'value': value,
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                'gasPrice': self.web3.eth.gas_price,
                'gas': 100000
            }
            gas = self.web3.eth.estimate_gas(txn)
            txn.update({'gas': gas})

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            hash_ = str(Web3.to_hex(tx_hash))
            time.sleep(15)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')            
            else:
                self.log.info('Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, f'Send {val} ETH YourSelf', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.send(amount_eth, retry)
                return

            self.log.info(f'[{self.number}]Send {val} ETH YourSelf || https://explorer.zksync.io/tx/{hash_}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Send {val} ETH YourSelf', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, f'Send {val} ETH YourSelf', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.send(amount_eth, retry)

        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, f'Send {val} ETH YourSelf', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.send(amount_eth, retry)

        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, f'Send {val} ETH YourSelf', self.address_wallet,
                                                 'insufficient funds')
                    return 'balance'
            else:
                self.log.info(error)
                time.sleep(120)
                retry += 1
                if retry > 5:
                    return 0
                self.send(amount_eth, retry)
