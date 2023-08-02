from web3 import Web3
import json as js
import time
from utils.approve import Approve
from eth_abi import encode
from requests import ConnectionError
from utils.tg_bot import TgBot
from web3.exceptions import TransactionNotFound


class SynkSwap(Approve, TgBot):

    """  """

    def __init__(self, private_key, web3, number, log):
        super().__init__(private_key, web3, number, log)
        self.web3 = web3
        self.number = number
        self.log = log
        self.address = Web3.to_checksum_address('0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295')
        self.abi = js.load(open('./abi/syncswap_router.txt'))
        self.abi_pool = js.load(open('./abi/syncswap_pool.txt'))
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)
        self.private_key = private_key
        self.address_wallet = self.web3.eth.account.from_key(private_key).address
        self.ETH = Web3.to_checksum_address('0x5aea5775959fbc2557cc8789bc1bf90a239d9a91')
        self.token_abi = js.load(open('./abi/erc20.txt'))
        self.get_pool_address = Web3.to_checksum_address('0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb')
        self.get_pool_abi = js.load(open('./abi/pool.txt'))
        self.contract_get_pool = self.web3.eth.contract(address=self.get_pool_address, abi=self.get_pool_abi)

    def buy_token(self, token_to_buy, value_eth, retry=0):
        self.log.info('Buy token Synkswap')
        try:
            balance = self.web3.eth.get_balance(self.address_wallet)
            value = Web3.to_wei(value_eth, 'ether')
            if value > balance:
                value = balance - Web3.to_wei(0.003, 'ether')
                if value < Web3.to_wei(0.000001, 'ether'):
                    self.log.info('Insufficient funds')
                    return 'balance'
            pool_address = self.contract_get_pool.functions.getPool(self.ETH, token_to_buy).call()
            contract_pool = self.web3.eth.contract(address=pool_address, abi=self.abi_pool)
            reserves = contract_pool.functions.getReserves().call()
            token_contract = self.web3.eth.contract(address=token_to_buy, abi=self.token_abi)
            decimal = token_contract.functions.decimals().call()
            data = encode(['address', 'address', 'uint8'], [self.ETH, self.address_wallet, 1])
            zero_address = '0x0000000000000000000000000000000000000000'
            steps = [
                {
                    'pool': pool_address,
                    'data': data,
                    'callback': zero_address,
                    'callbackData': '0x'
                }
            ]
            [reserves_usdc, reserves_eth] = reserves
            reserves_usdc = reserves_usdc / 10e6
            reserves_eth = reserves_eth / 10e18
            price_one_token = reserves_eth / reserves_usdc
            min_tokens = int(float(Web3.from_wei(value, 'ether')) / price_one_token * 0.97 * 10 ** decimal)
            min_tok = round(Web3.from_wei(min_tokens, 'picoether'), 3)
            paths = [
                {
                    'steps': steps,
                    'tokenIn': zero_address,
                    'amountIn': value
                }
            ]
            contract_txn = self.contract.functions.swap(
                paths,
                min_tokens,
                (int(time.time()) + 10000)  # deadline
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
                self.log.info(f'Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'Buy token Synkswap', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.buy_token(token_to_buy, value_eth, retry)
                return

            hash_ = str(tx_hash.hex())
            self.log.info(f'[{self.number}] Buy {min_tok} USDC Synkswap || https://explorer.zksync.io/tx/{hash_}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Buy {min_tok} USDC Synkswap', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Buy token Synkswap', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.buy_token(token_to_buy, value_eth, retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Buy token Synkswap', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.buy_token(token_to_buy, value_eth, retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, 'Buy token Synkswap', self.address_wallet,
                                                 'insufficient funds')
                    return 'balance'
            else:
                self.log.info(error)
                time.sleep(120)
                retry += 1
                if retry > 5:
                    return 0
                self.buy_token(token_to_buy, value_eth, retry)

    def sold_token(self, token_to_sold, retry=0):
        self.log.info('Sold token Synkswap')
        try:
            token_contract = self.web3.eth.contract(address=token_to_sold, abi=self.token_abi)
            decimal = token_contract.functions.decimals().call()
            balance = token_contract.functions.balanceOf(self.address_wallet).call()
            if balance == 0:
                self.log.info('Balance USDC - 0\n')
                return
            min_tok = round(Web3.from_wei(balance, 'picoether'), 3)
            pool_address = self.contract_get_pool.functions.getPool(token_to_sold, self.ETH).call()
            contract_pool = self.web3.eth.contract(address=pool_address, abi=self.abi_pool)
            reserves = contract_pool.functions.getReserves().call()
            data = encode(['address', 'address', 'uint8'], [token_to_sold, self.address_wallet, 1])
            zero_address = '0x0000000000000000000000000000000000000000'
            steps = [
                {
                    'pool': pool_address,
                    'data': data,
                    'callback': zero_address,
                    'callbackData': '0x'
                }
            ]
            [reserves_usdc, reserves_eth] = reserves
            reserves_usdc = reserves_usdc / 10e6
            reserves_eth = reserves_eth / 10e18
            price_one_token = reserves_usdc / reserves_eth
            min_tokens = Web3.to_wei(float(balance / 10 ** decimal) / price_one_token * 0.97, 'ether')
            paths = [
                {
                    'steps': steps,
                    'tokenIn': token_to_sold,
                    'amountIn': balance
                }
            ]
            allowance = token_contract.functions.allowance(self.address_wallet, self.address).call()
            if allowance < 1000000 * 10 ** decimal:
                self.log.info('Waiting for approve')
                self.approve(token_to_sold, self.address)
                time.sleep(60)

            contract_txn = self.contract.functions.swap(
                paths,
                min_tokens,
                (int(time.time()) + 10000)  # deadline
            ).build_transaction({
                'from': self.address_wallet,
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
                self.log.info(f'Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'Sold token Synkswap', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.sold_token(token_to_sold, retry)
                return

            hash_ = str(tx_hash.hex())
            self.log.info(f'[{self.number}] Sold {min_tok} USDC Synkswap || https://explorer.zksync.io/tx/{hash_}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Sold {min_tok} USDC Synkswap', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Sold token Synkswap', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.sold_token(token_to_sold, retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Sold token Synkswap', self.address_wallet,
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
                        TgBot.send_message_error(self, self.number, 'Sold token Synkswap', self.address_wallet,
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
        self.log.info('Add Liquidity Synkswap')
        try:
            token_contract = self.web3.eth.contract(address=token_to_add, abi=self.token_abi)
            token_balance = token_contract.functions.balanceOf(self.address_wallet).call()
            decimal = token_contract.functions.decimals().call()
            value = float(token_balance / 10 ** decimal)
            min_tok = round(Web3.from_wei(token_balance, 'picoether'), 3)
            pool_address = self.contract_get_pool.functions.getPool(token_to_add, self.ETH).call()
            contract_pool = self.web3.eth.contract(address=pool_address, abi=self.abi_pool)
            reserves = contract_pool.functions.getReserves().call()
            native_eth_address = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")
            data = encode(
                ["address"],
                [self.address_wallet]
            )
            [reserves_usdc, reserves_eth] = reserves
            reserves_usdc = reserves_usdc / 10e6
            reserves_eth = reserves_eth / 10e18
            price_one_token = reserves_eth / reserves_usdc
            value_eth_ = price_one_token * value
            value_eth = Web3.to_wei(value_eth_, 'ether')
            min_liquidity = int(value * 0.95 * 10 ** decimal)
            value = int(value * 10 ** decimal)
            allowance = token_contract.functions.allowance(self.address_wallet, self.address).call()
            if allowance < 1000000 * 10 ** decimal:
                self.log.info('Waiting for approve')
                self.approve(token_to_add, self.address)
                time.sleep(60)

            contract_txn = self.contract.functions.addLiquidity2(
                pool_address,
                [(token_to_add, value), (native_eth_address, value_eth)],
                data,
                min_liquidity,
                native_eth_address,
                '0x'
            ).build_transaction(
                {
                    'from': self.address_wallet,
                    'gasPrice': self.web3.eth.gas_price,
                    'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                    'value': value_eth
                }
            )
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
                    TgBot.send_message_error(self, self.number, 'Add Liquidity Synkswap', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.add_liquidity(token_to_add, retry)
                return
            hash_ = str(tx_hash.hex())
            self.log.info(f'[{self.number}] Add {min_tok} USDC Liquidity Synkswap || https://explorer.zksync.io/tx/{hash_}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Add {min_tok} USDC Liquidity Synkswap', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Add Liquidity Synkswap', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.add_liquidity(token_to_add, retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Add Liquidity Synkswap', self.address_wallet,
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
                        TgBot.send_message_error(self, self.number, 'Add Liquidity Synkswap', self.address_wallet,
                                                 'insufficient funds')
                    return 'balance'
            else:
                self.log.info(error)
                time.sleep(120)
                retry += 1
                if retry > 5:
                    return 0
                self.add_liquidity(token_to_add, retry)
