import logging
import os

from dotenv import load_dotenv

from bot import TelegramBot, SubscriberManager

 
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# loading environment variables
load_dotenv()

if __name__ == '__main__':
    subscriber_manager = SubscriberManager(file_name=os.environ.get('SUBSCRIBERS_PATH'))
    subscriber_manager.init()

    level_manager = Level

    bot = TelegramBot(token=os.environ.get('TELEGRAM_TOKEN'), subscriber_manager=subscriber_manager)
    bot.init()
    bot.start()
