import logging
import os

from dotenv import load_dotenv

from bot import TelegramBot

 
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# loading environment variables
load_dotenv()

if __name__ == '__main__':
    bot = TelegramBot(token=os.environ.get('TELEGRAM_TOKEN'))
    bot.init()
    bot.start()
