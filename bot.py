import os

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ChatMemberHandler


class TelegramBot:

    def __init__(self, token):
        self.application = ApplicationBuilder().token(token).build()

    def init(self):
        self._init_handlers()

    def start(self):
        self.application.run_polling()

    async def _chat_member_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = 'Welcome to the *Water Sensor Bot*!\n\nThis bot was developed to notify you about the high level of water in a bucket on the balcony.\n\nTo subscribe for updates type /subscribe\n\n.For full list of commands type /help.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    def _remove_job_if_exists(self, name: str, context: ContextTypes.DEFAULT_TYPE):
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_jobs:
            return False
        for job in current_jobs:
            job.schedule_removal()
        return True

    async def _subscribe_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        self._remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(self._level_alarm, 
                                        interval=int(os.environ.get('LEVEL_POLLING_INTERVAL', 3600)), 
                                        chat_id = chat_id, 
                                        name=str(chat_id))
        
        msg = 'You have successfully subscribed for notifications! To unsubscribe type /unsubscribe'
        await update.effective_message.reply_text(chat_id=chat_id, text=msg)

    async def _unsubscribe_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self._remove_job_if_exists(str(chat_id), context)
        msg = 'You\'ve ubsubscribed from notifications. To subscribe type /subscribe.'
        await update.effective_message.reply_text(chat_id=chat_id, text=msg)

    def _get_water_level(self):
        file = open(os.environ.get('LEVEL_PATH'), 'r')
        level = file.read()
        file.close()
        return level

    async def _level_alarm(self, context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        level = self._get_water_level()

        if float(level) > float(os.environ.get('LEVEL_LIMIT', 0)):
            return

        msg = '*ALARM!* Current water level: {level} cm.'.format(level=level.strip())
        await context.bot.send_message(job.chat_id, text=msg)

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

    def _init_handlers(self):
        # new chat member
        self.application.add_handler(ChatMemberHandler(self._chat_member_handler, ChatMemberHandler.CHAT_MEMBER))

        # commands
        self.application.add_handler(CommandHandler('subscribe', self._subscribe_handler))
        self.application.add_handler(CommandHandler('unsubscribe', self._unsubscribe_handler))
        self.application.add_handler(CommandHandler('help', self._help_handler))
        self.application.add_handler(CommandHandler('level', self._level_handler))

        # fallback handler
        self.application.add_handler(MessageHandler(filters.ALL, self._unknow_handler))

    