from web3 import Web3
import json as js
import time
from utils.approve import Approve
from requests import ConnectionError
from utils.tg_bot import TgBot
from web3.exceptions import TransactionNotFound


class MuteSwap(Approve, TgBot):

    """ https://app.mute.io/swap """

    def __init__(self, private_key, web3, number, log):
        super().__init__(private_key, web3, number, log)
        self.web3 = web3
        self.log = log
        self.number = number
        self.address = Web3.to_checksum_address('0x8B791913eB07C32779a16750e3868aA8495F5964')
        self.abi = js.load(open('./abi/mute.txt'))
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)
        self.private_key = private_key
        self.address_wallet = self.web3.eth.account.from_key(private_key).address
        self.ETH = Web3.to_checksum_address('0x5aea5775959fbc2557cc8789bc1bf90a239d9a91')
        self.token_abi = js.load(open('./abi/erc20.txt'))

    def buy_token(self, token_to_buy, amount_eth, retry=0):
        self.log.info('Buy token MuteSwap')
        try:
            balance = self.web3.eth.get_balance(self.address_wallet)
            value = Web3.to_wei(amount_eth, 'ether')
            if value > balance:
                value = balance - Web3.to_wei(0.003, 'ether')
                if value < Web3.to_wei(0.000001, 'ether'):
                    self.log.info('Insufficient funds')
                    return 'balance'
            amount_out = self.contract.functions.getAmountsOut(value, [self.ETH, token_to_buy], [False, True]).call()[1]
            min_tokens = int(amount_out * (1 - (1 / 100)))
            min_tok = round(Web3.from_wei(min_tokens, 'picoether'), 3)
            contract_txn = self.contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                min_tokens,
                [self.ETH, token_to_buy],
                self.address_wallet,
                (int(time.time()) + 10000),  # deadline
                [False, True]
            ).build_transaction({
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
                self.buy_token(token_to_buy, amount_eth, retry)
                return

            hash_ = str(tx_hash.hex())
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Buy {min_tok} USDC MuteSwap', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
            self.log.info(f'[{self.number}] Buy {min_tok} USDC MuteSwap || https://explorer.zksync.io/tx/{hash_}\n')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Buy token MuteSwap', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.buy_token(token_to_buy, amount_eth, retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Buy token MuteSwap', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.buy_token(token_to_buy, amount_eth, retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient balance' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, 'Buy token MuteSwap', self.address_wallet,
                                                 'insufficient funds')
                    return 'balance'
            else:
                self.log.info(error)
                time.sleep(120)
                retry += 1
                if retry > 5:
                    return 0
                self.buy_token(token_to_buy, amount_eth, retry)

    def sold_token(self, token_to_sold, retry=0):
        try:
            self.log.info('Sold token MuteSwap')
            token_contract = self.web3.eth.contract(address=token_to_sold, abi=self.token_abi)
            token_balance = token_contract.functions.balanceOf(self.address_wallet).call()
            amount_out = self.contract.functions.getAmountsOut(token_balance, [token_to_sold, self.ETH], [False, False]).call()[1]
            min_tokens = int(amount_out * (1 - (1 / 100)))
            min_tok = round(Web3.from_wei(token_balance, 'picoether'), 3)
            decimal = token_contract.functions.decimals().call()
            allowance = token_contract.functions.allowance(self.address_wallet, self.address).call()
            if allowance < 1000000 * 10 ** decimal:
                self.log.info('Waiting for approve')
                self.approve(token_to_sold, self.address)
                time.sleep(60)
            dick = {
                'from': self.address_wallet,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            }
            contract_txn = self.contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                token_balance,
                min_tokens,
                [token_to_sold, self.ETH],
                self.address_wallet,
                (int(time.time()) + 10000),  # deadline
                [False, False]
            ).build_transaction(dick)
            signed_txn = self.web3.eth.account.sign_transaction(contract_txn, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(15)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')            
            else:
                self.log.info(f'Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'Sold token Mute', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.sold_token(token_to_sold, retry)
                return
            hash_ = str(tx_hash.hex())
            self.log.info(f'[{self.number}] Sold {min_tok} USDC MuteSwap || https://explorer.zksync.io/tx/{hash_}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Sold {min_tok} USDC MuteSwap', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Sold token MuteSwap', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.sold_token(token_to_sold, retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Sold token MuteSwap', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.sold_token(token_to_sold, retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, 'Sold token MuteSwap', self.address_wallet,
                                                 'insufficient funds')
                    return 'balance'
            else:
                self.log.info(error)
                time.sleep(120)
                retry += 1
                if retry > 5:
                    return 0
                self.sold_token(token_to_sold, retry)

    def add_liquidity(self, token_to_add, retry=0):
        self.log.info('Add Liquidity Mute')
        try:
            token_contract = self.web3.eth.contract(address=token_to_add, abi=self.token_abi)
            token_balance = token_contract.functions.balanceOf(self.address_wallet).call()
            decimal = token_contract.functions.decimals().call()
            value = token_balance
            min_tok = round(Web3.from_wei(token_balance, 'picoether'), 3)
            amount_out_eth = self.contract.functions.getAmountsOut(value, [token_to_add, self.ETH], [True, False]).call()[1]
            allowance = token_contract.functions.allowance(self.address_wallet, self.address).call()
            if allowance < 100000 * 10 ** decimal:
                self.log.info('Waiting for approve')
                self.approve(token_to_add, self.address)
                time.sleep(60)
            contract_txn = self.contract.functions.addLiquidityETH(
                token_to_add,
                value,
                int(value * 0.95),
                int(amount_out_eth * 0.95),
                self.address_wallet,
                (int(time.time()) + 10000),  # deadline
                50,
                False
            ).build_transaction({
                'from': self.address_wallet,
                'value': amount_out_eth,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            })
            signed_txn = self.web3.eth.account.sign_transaction(contract_txn, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(15)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')            
            else:
                self.log.info(f'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.add_liquidity(token_to_add, retry)
                return
            hash_ = str(tx_hash.hex())
            self.log.info(f'[{self.number}] Add {min_tok} USDC Liquidity || https://explorer.zksync.io/tx/{hash_}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Add  {min_tok} USDC Liquidity Mute', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Main Bridge', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.add_liquidity(token_to_add, retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Add Liquidity Mute', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.add_liquidity(token_to_add, retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, 'Add Liquidity Mute', self.address_wallet,
                                                 'insufficient funds')
                    return 'balance'
            else:
                self.log.info(error)
                time.sleep(120)
                retry += 1
                if retry > 5:
                    return 0
                self.add_liquidity(token_to_add, retry)
