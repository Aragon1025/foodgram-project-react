import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class TelegramHandler(logging.Handler):
    def __init__(self, token, chat_id):
        super().__init__()
        self.token = token
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        data = {'chat_id': self.chat_id, 'text': log_entry}
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print('Не удалось отправить сообщение в Telegram:', response.text)

    def send_initial_message(self):
        initial_message = (
            "Привет, я ваш бот логов Foodgram\n"
            "Наш сайт находится по адресу https://aragon.servebeer.com"
        )
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        data = {'chat_id': self.chat_id, 'text': initial_message}
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print('Не удалось отправить начальное сообщение в Telegram:', 
                  response.text)


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

telegram_handler = TelegramHandler(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
