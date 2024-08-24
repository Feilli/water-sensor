import os

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ChatMemberHandler

from helpers import set_interval, start_interval


class TelegramBot:

    def __init__(self, token):
        self.application = ApplicationBuilder().token(token).build()

    async def init(self):
        self.init_handlers()
        self.init_water_level_polling()

    def start(self):
        self.application.run_polling()

    async def _chat_member_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = 'Welcome to the Framaizon ChatBot!\n\nThis bot was developed to notify you about the high level of water in a bucket on the balcony.\n\nTo subscribe for updates type /subscribe\n\n.For full list of commands type /help.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    def _add_subscriber(self, subscriber):
        file = open(os.environ.get('SUBSCRIBERS_PATH'), 'w+')
        file.write(str(subscriber))
        file.close()

    async def _subscribe_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self._add_subscriber(subscriber=update.effective_chat.id)
        msg = 'You\'ve subscribed to notifications. To unsubscribe type /unsubscribe.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    def _remove_subscriber(self, subscriber):
        # read subscribers from file
        with open(os.environ.get('SUBSCRIBERS_PATH', 'r')) as file:
            subscribers = file.readlines()

        # rewrite the list of subscribers
        with open(os.environ.get('SUBSCRIBERS_PATH', 'w')) as file:
            for sub in subscribers:
                if sub.strip('\n') != subscriber:
                    file.write(sub)

    async def _unsubscribe_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self._remove_subscriber(update.effective_chat.id)
        msg = 'You\'ve ubsubscribed from notifications. To subscribe type /subscribe.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    def _get_water_level(self):
        file = open(os.environ.get('LEVEL_PATH'), 'r')
        level = file.read()
        file.close()
        return level
    
    def _get_subscribers(self): 
        file = open(os.environ.get('SUBSCRIBERS_PATH'), 'r')
        subscribers = file.readlines()
        file.close()
        return subscribers
    
    @set_interval(os.environ.get('LEVEL_POLLING_INTERVAL', 3600))
    async def init_water_level_polling(self):
        level = self._get_water_level()

        if float(level) > float(os.environ.get('LEVEL_LIMIT', 0)):
            return

        chats = self._get_subscribers()
        msg = 'Current water level: {level} cm.'.format(level=level.strip())

        for chat in chats:
            await self.application.bot.send_message(chat_id=chat, text=msg)

    async def _level_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        level = self._get_water_level()
        msg = 'Current water level: {level} cm.'.format(level=level.strip())
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    async def _help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = 'Available commands:\n/help\n/subscribe\n/ubsubscribe\n/level'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    async def _unknow_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = 'Unknown command.\n\nType /help to list all commands.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    def init_handlers(self):
        # new chat member
        self.application.add_handler(ChatMemberHandler(self._chat_member_handler, ChatMemberHandler.CHAT_MEMBER))

        # commands
        self.application.add_handler(CommandHandler('subscribe', self._subscribe_handler))
        self.application.add_handler(CommandHandler('unsubscribe', self._unsubscribe_handler))
        self.application.add_handler(CommandHandler('help', self._help_handler))
        self.application.add_handler(CommandHandler('level', self._level_handler))

        # fallback handler
        self.application.add_handler(MessageHandler(filters.ALL, self._unknow_handler))

    