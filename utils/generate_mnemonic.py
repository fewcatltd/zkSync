from eth_account import Account

Account.enable_unaudited_hdwallet_features()
account = Account.create_with_mnemonic()

print(account[1])
