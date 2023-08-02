from web3 import Web3
from eth_account import Account

def generate_ethereum_private_keys(num_addresses, mnemonic):
    Account.enable_unaudited_hdwallet_features()
    words = mnemonic.strip().split()
    if len(words) != 12:
        raise ValueError("Мнемоника должна состоять из 12 слов.")

    private_keys = []

    for i in range(num_addresses):
        account = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{i}")
        private_key = account.key
        private_keys.append(private_key.hex())

    return private_keys

if __name__ == "__main__":
    try:
        num_addresses = int(input("Сколько адресов сгенерировать? "))
        if num_addresses <= 0:
            print("Введите число больше 0.")
            exit(1)

        mnemonic = input("Введите мнемонику (12 слов): ")
        private_keys = generate_ethereum_private_keys(num_addresses, mnemonic)

        print("\nПриватные ключи:")
        for idx, key in enumerate(private_keys, start=1):
            print(f"{key}")
    except ValueError:
        print("Некорректный ввод. Пожалуйста, введите целое число и верную мнемонику из 12 слов.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")