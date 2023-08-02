from web3 import Web3
import time
from requests import ConnectionError
from utils.tg_bot import TgBot
from web3.exceptions import TransactionNotFound


class Orbiter(TgBot):
    def __init__(self, private_key, web3, number, log, scan):
        self.log = log
        self.scan = scan
        self.private_key = private_key
        self.web3 = web3
        self.number = number
        self.account = self.web3.eth.account.from_key(private_key)
        self.address_wallet = self.account.address
        self.address = Web3.to_checksum_address('0x80C67432656d59144cEFf962E8fAF8926599bCF8')
        self.ORBITER_AMOUNT_STR = {
            'ethereum'      : '9001',
            'optimism'      : '9007',
            'arbitrum'      : '9002',
            'zksync'        : '9014',
        }

    def get_orbiter_value(self, base_num, chain):
        difference = str(base_num)[:-4]
        difference += self.ORBITER_AMOUNT_STR[chain]
        return int(difference)

    def bridge(self, value_eth, chain_to, retry=0):
        self.log.info(f'Orbiter bridge to {chain_to["name"]}')
        try:
            if chain_to['name'] == 'zksync':
                min_value_bridge = Web3.to_wei(0.0066, 'ether')
                value_bridge = Web3.to_wei(value_eth + 0.0016, 'ether')
                balance = self.web3.eth.get_balance(self.address_wallet)
                if balance < value_bridge:
                    value_bridge = int(balance * 0.9)
                if value_bridge < min_value_bridge:
                    self.log.info('Insufficient balance')
                    return 0
                amount = round(Web3.from_wei(value_bridge, 'ether'), 4)
                value_bridge = self.get_orbiter_value(value_bridge, chain_to['name'])

                contract_tx = {
                    'chainId': self.web3.eth.chain_id,
                    'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                    'from': self.address_wallet,
                    'to': self.address,
                    'value': value_bridge,
                    'gasPrice': self.web3.eth.gas_price
                }
            elif chain_to['name'] == 'arbitrum':
                min_value_bridge = Web3.to_wei(0.0063, 'ether')
                value_bridge = Web3.to_wei(value_eth + 0.0016, 'ether')
                balance = self.web3.eth.get_balance(self.address_wallet)
                if balance < value_bridge:
                    value_bridge = int(balance * 0.9)
                if value_bridge < min_value_bridge:
                    self.log.info('Insufficient balance')
                    return 0
                amount = round(Web3.from_wei(value_bridge, 'ether'), 4)
                value_bridge = self.get_orbiter_value(value_bridge, chain_to['name'])
                contract_tx = {
                    'chainId': self.web3.eth.chain_id,
                    'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                    'from': self.address_wallet,
                    'to': self.address,
                    'value': value_bridge,
                    'gasPrice': self.web3.eth.gas_price
                }
            else:
                min_value_bridge = Web3.to_wei(0.0066, 'ether')
                value_bridge = Web3.to_wei(value_eth + 0.0016, 'ether')
                balance = self.web3.eth.get_balance(self.address_wallet)
                if balance < value_bridge:
                    value_bridge = int(balance * 0.9)
                if value_bridge < min_value_bridge:
                    self.log.info('Insufficient balance')
                    return 0
                amount = round(Web3.from_wei(value_bridge, 'ether'), 5)
                value_bridge = self.get_orbiter_value(value_bridge, chain_to['name'])
                contract_tx = {
                    'chainId': self.web3.eth.chain_id,
                    'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                    'from': self.address_wallet,
                    'to': self.address,
                    'value': value_bridge,
                    'gasPrice': self.web3.eth.gas_price,
                    'gas': 0
                }
            gas = self.web3.eth.estimate_gas(contract_tx)
            contract_tx.update({'gas': gas})
            signed_txn = self.web3.eth.account.sign_transaction(contract_tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(5)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')
            else:
                self.log.info('Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'Orbiter Bridge', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.bridge(value_eth, chain_to, retry)
                return

            hash_ = str(tx_hash.hex())
            self.log.info(f'Orbiter bridge {amount} eth complete\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Orbiter Bridge {amount} eth\n', self.address_wallet,
                                           f'{self.scan}{hash_}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Orbiter Bridge', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.bridge(value_eth, chain_to, retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Orbiter Bridge', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.bridge(value_eth, chain_to, retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, 'Orbiter Bridge', self.address_wallet,
                                                 'insufficient funds')
                    return 0
            self.log.info(error)

