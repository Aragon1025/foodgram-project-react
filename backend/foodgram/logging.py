import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
    class TelegramHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
            data = {'chat_id': TELEGRAM_CHAT_ID, 'text': log_entry}
            response = requests.post(url, data=data)
            if response.status_code != 200:
                print('Failed to send log message to Telegram:', response.text)

    telegram_handler = TelegramHandler()
    telegram_handler.setLevel(logging.ERROR)

    root_logger = logging.getLogger()
    root_logger.addHandler(telegram_handler)
else:
    print("Токен Telegram или ID чата не указаны. Логирование в Telegram не будет включено.")

logger = logging.getLogger(__name__)
logger.error("Привет, я ваш бот логов Foodgram")
logger.error("Привет, я ваш бот логов Foodgram\n"
             "Наш сайт находится по адресу https://aragon.servebeer.com")
