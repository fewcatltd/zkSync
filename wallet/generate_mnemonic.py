from eth_account import Account

def generate_mnemonic():
    Account.enable_unaudited_hdwallet_features()
    passphrase = input("Введите пароль для генерации мнемоники: ")
    account = Account.create_with_mnemonic(passphrase=passphrase)

    return account[1]

if __name__ == "__main__":
    try:
        mnemonic = generate_mnemonic()

        print("\nМнемоника:", mnemonic)
    except Exception as e:
        print(f"Произошла ошибка: {e}")