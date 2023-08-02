from web3 import Web3
import json as js
import time
from utils.tg_bot import TgBot
from web3.exceptions import TransactionNotFound


class Approve(TgBot):
    def __init__(self, private_key, web3, number, log):
        self.private_key = private_key
        self.number = number
        self.log = log
        self.web3 = web3
        self.address_wallet = self.web3.eth.account.from_key(private_key).address
        self.token_abi = js.load(open('./abi/erc20.txt'))

    def approve(self, token_to_approve, address_to_approve, retry=0):
        token_contract = self.web3.eth.contract(address=token_to_approve, abi=self.token_abi)
        max_amount = Web3.to_wei(2 ** 64 - 1, 'ether')
        dick = {
            'from': self.address_wallet,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
        }
        try:
            txn = token_contract.functions.approve(address_to_approve, max_amount).build_transaction(dick)
            signed_tx = self.web3.eth.account.sign_transaction(txn, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(5)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')
            else:
                self.log.info(f'Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'approve', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.approve(token_to_approve, address_to_approve, retry)
                return

            self.log.info(f'[{self.number}] approve || https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, 'approve', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'approve', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.approve(token_to_approve, address_to_approve, retry)

        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'approve', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.approve(token_to_approve, address_to_approve, retry)

        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, 'approve', self.address_wallet,
                                                 'insufficient funds')
                    return 0
            self.log.info(error)
