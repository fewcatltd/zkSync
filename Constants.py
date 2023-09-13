import os
from dotenv import load_dotenv

load_dotenv('./.env')

def toBoolean(value):
    return value.lower() == 'true' or value.lower() == 'yes' or value.lower() == '1'

# General Settings ---------------------------------------------------------------------------------------------------------------------------------------------------

tg_bot_send = toBoolean(os.getenv('TG_BOT_SEND'))                       # Включить уведомления в тг или нет                              [True or False]
tg_token    = os.getenv('TG_TOKEN')                                     # API токен тг-бота - создать его можно здесь - https://t.me/BotFather
tg_id       = int(os.getenv('TG_ID'))                                   # id твоего телеграмма можно узнать тут https://t.me/getmyid_bot

shuffle_wallets = toBoolean(os.getenv('SHUFFLE_WALLETS'))               # Мешать кошельки                                                [True or False]

number_of_threads = int(os.getenv('THREADS'))                           # Количество потоков

delay_between_tx_min = int(os.getenv('DELAY_BETWEEN_TX_MIN'))           # Максимальная и
delay_between_tx_max = int(os.getenv('DELAY_BETWEEN_TX_MAX'))           # Минимальная задержка между транзакциями. Секунды

RPC_ZKSYNK   = os.getenv('RPC_ZKSYNK')                                  # Можно выбрать ещё две RPC -- 'https://rpc.ankr.com/zksync_era' или 'https://zksync-era.rpc.thirdweb.com'
RPC_ARBITRUM = os.getenv('RPC_ARBITRUM')                                #
RPC_OPTIMISM = os.getenv('RPC_OPTIMISM')                                #
RPC_ETH      = os.getenv('RPC_ETH')                                     #

# eth_bridge https://bridge.zksync.io ------------------------------------------------------------------------------------------------------------------------------

value_bridge_eth_min = float(os.getenv('VALUE_BRIDGE_ETH_MIN'))         # Минимальное и
value_bridge_eth_max = float(os.getenv('VALUE_BRIDGE_ETH_MAX'))         # Максимальное значение -> Будет рандомное среднее
                                                                        # Если сумма больше, чем есть на аккаунте, будет бридж всего баланса

min_token = 0.001               # Сколько ETH оставлять на аккаунте

decimal = int(os.getenv('DECIMAL'))                     # Округление, количество знаков после запятой для суммы бриджа

max_gas = int(os.getenv('MAX_GAS'))                     # Чекер газа - если выше заданного значения, софт будет ждать -- данная настройка работает для всех модулей

# orbiter (min 0.005 eth) -------------------------------------------------------------------------------------------------------------------------------------

CHAIN_FROM = os.getenv('CHAIN_FROM')         # Из какой сети
CHAIN_TO   = os.getenv('CHAIN_TO')           # В какую сеть
                                # На выбор 3 сети   [Arbitrum, ZkSynk, Optimism]

orbiter_bridge_eth_min = float(os.getenv('ORBITER_BRIDGE_ETH_MIN'))   # Минимальное и
orbiter_bridge_eth_max = float(os.getenv('ORBITER_BRIDGE_ETH_MAX'))   # Максимальное значение -> Будет рандомное среднее

orbiter_decimal = int(os.getenv('ORBITER_DECIMAL'))                   # Округление, количество знаков после запятой

# defi_module --------------------------------------------------------------------------------------------------------------------------------------------------------------

buy_usdc_at_the_end = toBoolean(os.getenv('BUY_USDC_AT_THE_END'))      # Покупа USDC в конце свапов             [True or False]

mute_swap = toBoolean(os.getenv('MUTE_SWAP'))                          # https://app.mute.io/swap               [True or False]
space_fi  = toBoolean(os.getenv('SPACE_FI'))                           # https://swap-zksync.spacefi.io/#/swap  [True or False]
velocore  = toBoolean(os.getenv('VELOCORE'))                           # https://app.velocore.xyz/swap          [True or False]
syncswap  = toBoolean(os.getenv('SYNCSWAP'))                           # https://syncswap.xyz/                  [True or False]
symbiosis = toBoolean(os.getenv('SYMBIOSIS'))                          # https://app.symbiosis.finance/         [True or False]
one_inch  = toBoolean(os.getenv('ONE_INCH'))                           # https://app.1inch.io/                  [True or False]

value_swap_min = float(os.getenv('VALUE_SWAP_MIN'))                    # Минимальное и
value_swap_max = float(os.getenv('VALUE_SWAP_MAX'))                    # Максимальное значение -> Будет рандомное среднее

swap_decimal = int(os.getenv('SWAP_DECIMAL'))                          # Округление, количество знаков после запятой

number_of_repetitions = int(os.getenv('NUMBER_OF_REPETITIONS'))        # Количество повторений свапов (Кругов)

# defi_module liquidity ---------------------------------------------------------------------------------------------------------------------------------------------------------

liquiditi_syncswap  = toBoolean(os.getenv('LIQUIDITI_SYNCSWAP'))        # Ликвидность https://syncswap.xyz      [True or False]
liquiditi_mute      = toBoolean(os.getenv('LIQUIDITI_MUTE'))            # Ликвидность https://app.mute.io/swap  [True or False]

liquidity_value_min = float(os.getenv('LIQUIDITY_VALUE_MIN'))           # Минимальное и
liquidity_value_max = float(os.getenv('LIQUIDITY_VALUE_MAX'))           # Максимальное значение -> Будет рандомное среднее

liquidity_decimal   = int(os.getenv('LIQUIDITY_DECIMAL'))               # Округление, количество знаков после запятой

# nft -------------------------------------------------------------------------------------------------------------------------------------------------------

mint_era_name_domain = toBoolean(os.getenv('MINT_ERA_NAME_DOMAIN'))    # Минт доменного имени era.name за 0.003 ETH                                        [True or False]
domen_name_service   = toBoolean(os.getenv('DOMEN_NAME_SERVICE'))      # Минт доменного имени ZKNS за +-0.003 ETH                                          [True or False]

layerzero_nft_bridge = toBoolean(os.getenv('LAYERZERO_NFT_BRIDGE'))    # Минт и бридж NFT через LayerZero - минт доллар, отправка 1.5                      [True or False]
random_chain_nft     = toBoolean(os.getenv('RANDOM_CHAIN_NFT'))        # Если random_chain_nft = True то будет бридж в рандомную сеть                      [True or False]
chain_list_nft       = [int(chain) for chain in os.getenv('CHAIN_LIST_NFT').split(',')]    # Список сетей на рандомный выбор, можно удалить дорогую, ниже представлен список
dst_chain_nft        = int(os.getenv('DST_CHAIN_NFT'))                 # На выбор, если random_chain_nft = False

lz_message           = toBoolean(os.getenv('LZ_MESSAGE'))             # Отправка сообщения layer0                                                          [True or False]
random_chain         = toBoolean(os.getenv('RANDOM_CHAIN'))           # Если random_chain = True то будет рандомная сеть                                   [True or False]
chain_list_message   = [int(chain) for chain in os.getenv('CHAIN_LIST_MESSAGE').split(',')]  # Список сетей на рандомный выбор, можно удалить дорогую, ниже представлен список

dst_chain            = int(os.getenv('DST_CHAIN'))                    # На выбор, если random_chain = False

# self_mixer -----------------------------------------------------------------------------------------------------------------------

value_send_min = float(os.getenv('VALUE_SEND_MIN'))                   # Минимальное и
value_send_max = float(os.getenv('VALUE_SEND_MAX'))                   # Максимальное количество ETH -> Будет рандомное среднее

decimals_send = int(os.getenv('DECIMALS_SEND'))                       # Округление, количество знаков после запятой

number_transactions_min = int(os.getenv('NUMBER_TRANSACTIONS_MIN'))   # Минимальное и
number_transactions_max = int(os.getenv('NUMBER_TRANSACTIONS_MAX'))   # Максимальное количество транзакций -> Будет рандомное среднее

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
