from web3 import Web3
import json as js
import time
from requests import ConnectionError
from web3.exceptions import TransactionNotFound
from utils.tg_bot import TgBot


class MintAndBridge(TgBot):

    def __init__(self, private_key, web3, number, log):
        self.private_key = private_key
        self.web3 = web3
        self.number = number
        self.log = log
        self.account = self.web3.eth.account.from_key(private_key)
        self.address_wallet = self.account.address
        self.address = Web3.to_checksum_address('0xD43A183C97dB9174962607A8b6552CE320eAc5aA')
        self.abi = js.load(open('./abi/nft.txt'))
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

    def mint(self, retry=0):
        self.log.info('Mint nft')
        try:
            contract_tx = self.contract.functions.mint().build_transaction({
                'from': self.address_wallet,
                'value': Web3.to_wei(0.0005, 'ether'),
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                'gasPrice': self.web3.eth.gas_price
            })

            signed_txn = self.web3.eth.account.sign_transaction(contract_tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(15)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')            
            else:
                self.log.info(f'Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, 'Mint NFT', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.mint(retry)
                return
            hash_ = str(tx_hash.hex())
            self.log.info(f'Mint NFT || https://explorer.zksync.io/tx/{hash_}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, 'Mint NFT', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{hash_}')
            time.sleep(3)
            nft_id = self.get_nft_id(tx_hash)
            self.log.info(f'NTF ID - {nft_id}')
            return nft_id
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Mint NFT', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.mint(retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, 'Mint NFT', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.mint(retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, 'Mint NFT', self.address_wallet,
                                                 'insufficient funds')
                    return 0
            self.log.info(error)

    def get_nft_id(self, hash):
        tx_receipt = self.web3.eth.get_transaction_receipt(hash)
        if 'logs' in tx_receipt:
            logs = tx_receipt['logs']
        else:
            return 0

        for log in logs:
            try:
                if 'topics' in log and len(log['topics']) > 3:
                    topic = log['topics'][3]
                    nft_id = int(topic.hex(), 16)
                    return nft_id
                else:
                    continue
            except:
                return 0
        return 0

    def bridge(self, nft_id, chain, retry=0):
        self.log.info('Bridge nft')

        if chain == 158:
            data = '0xdc60fd9d2a4ccf97f292969580874de69e6c326ed43a183c97db9174962607a8b6552ce320eac5aa'
            value = Web3.to_wei(0.0013, 'ether')
            text = 'Polygon zkEVM'
        elif chain == 175:
            data = '0x5b10ae182c297ec76fe6fe0e3da7c4797cede02dd43a183c97db9174962607a8b6552ce320eac5aa'
            value = Web3.to_wei(0.0013, 'ether')
            text = 'Arbitrum Nova'
        elif chain == 176:
            data = '0x1a77bb02fba60251dccc1611e7321d7cf6f1feefd43a183c97db9174962607a8b6552ce320eac5aa'
            value = Web3.to_wei(0.0001, 'ether')
            text = 'Meter'
        elif chain == 112:
            data = '0x80be0f5b780e093b3f53bd5df8d1cf09aabf690fd43a183c97db9174962607a8b6552ce320eac5aa'
            value = Web3.to_wei(0.0004, 'ether')
            text = 'Fantom'
        elif chain == 110:
            data = '0x80be0f5b780e093b3f53bd5df8d1cf09aabf690fd43a183c97db9174962607a8b6552ce320eac5aa'
            value = Web3.to_wei(0.0005, 'ether')
            text = 'Arbitrum'
        elif chain == 102:
            data = '0xc162cf8c4c6697ab8e613ce0cd37c0ab97ba5a60d43a183c97db9174962607a8b6552ce320eac5aa'
            value = Web3.to_wei(0.0007, 'ether')
            text = 'BNB'
        elif chain == 111:
            data = '0xdc60fd9d2a4ccf97f292969580874de69e6c326ed43a183c97db9174962607a8b6552ce320eac5aa'
            value = Web3.to_wei(0.0007, 'ether')
            text = 'Optimism'
        elif chain == 106:
            data = '0x9539c9f145d2bf0eb7ed0824fe8583cd62410d3ed43a183c97db9174962607a8b6552ce320eac5aa'
            value = Web3.to_wei(0.0004, 'ether')
            text = 'Avax'
        else:
            data = '0xc162cf8c4c6697ab8e613ce0cd37c0ab97ba5a60d43a183c97db9174962607a8b6552ce320eac5aa'
            value = Web3.to_wei(0.0003, 'ether')
            text = 'Polygon'
        try:
            tx = self.contract.functions.crossChain(chain, data, nft_id).build_transaction({
                'from': self.address_wallet,
                'value': value,
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                'gasPrice': self.web3.eth.gas_price
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash = self.web3.to_hex(raw_tx_hash)
            self.log.info(f'Transaction sent: https://explorer.zksync.io/tx/{Web3.to_hex(tx_hash)}')
            time.sleep(15)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')            
            else:
                self.log.info(f'Transaction failed. Try again')
                if TgBot.TG_BOT_SEND is True:
                    TgBot.send_message_error(self, self.number, f'Bridge NFT from ZkSync to {text}', self.address_wallet,
                                             'Transaction failed. Try again')
                time.sleep(60)
                retry += 1
                if retry > 5:
                    return 0
                self.bridge(nft_id, chain, retry)
                return
            self.log.info(f'Bridge NFT from ZkSync to {text} || https://explorer.zksync.io/tx/{tx_hash}\n')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_success(self, self.number, f'Bridge NFT from ZkSync to {text}', self.address_wallet,
                                           f'https://explorer.zksync.io/tx/{tx_hash}')
        except TransactionNotFound:
            self.log.info('Transaction not found for a while. Try again')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, f'Bridge NFT from ZkSync to {text}', self.address_wallet,
                                         'Transaction not found for a while. Try again')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.bridge(nft_id, chain, retry)
        except ConnectionError:
            self.log.info('Connection error')
            if TgBot.TG_BOT_SEND is True:
                TgBot.send_message_error(self, self.number, f'Bridge NFT from ZkSync to {text}', self.address_wallet,
                                         'Connection error')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.bridge(nft_id, chain, retry)
        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    self.log.info('insufficient funds')
                    if TgBot.TG_BOT_SEND is True:
                        TgBot.send_message_error(self, self.number, f'Bridge NFT from ZkSync to {text}', self.address_wallet,
                                                 'insufficient funds')
                    return 0
            self.log.info(error)
