import logging
import asyncio
import os

from dotenv import load_dotenv

from bot import TelegramBot

 
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# loading environment variables
load_dotenv()

async def main():
    bot = TelegramBot(token=os.environ.get('TELEGRAM_TOKEN'))
    
    await bot.init()
    
    bot.start()

if __name__ == '__main__':
    asyncio.run(main())
