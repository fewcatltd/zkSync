import telebot
from Constants import *

class Telegram:
    TG_BOT_SEND = tg_bot_send                                                
    TG_TOKEN    = tg_token
    TG_ID       = tg_id 

class TgBot(Telegram):
    def send_message_success(self, number, text, address, link):
        try:
            str_send = f'[{number}]\n✅ {text}\nWallet: <a href="https://debank.com/profile/{address}" >{address}</a >\n<a href="{link}" >Tx hash</a > '
            bot = telebot.TeleBot(Telegram.TG_TOKEN)
            bot.send_message(Telegram.TG_ID, str_send, parse_mode='html', disable_web_page_preview=True)
        except Exception as error:
            print(error)

    def send_message_error(self, number, text, address, errorr):
        try:
            str_send = f'[{number}]\n❌ {text}\nWallet: <a href="https://debank.com/profile/{address}" >{address}</a >\n{errorr}'
            bot = telebot.TeleBot(Telegram.TG_TOKEN)
            bot.send_message(Telegram.TG_ID, str_send, parse_mode='html', disable_web_page_preview=True)
        except Exception as error:
            print(error)
