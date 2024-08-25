import os

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler


class SubscriberManager:

    def __init__(self, file_name='subscriber.txt'):
        self.file_name = file_name
        self.subscribers = []

    def init(self):
        with open(self.file_name, 'w+') as file:
            subscribers = file.readlines()

        for subscriber in subscribers:
            self.subscribers.append(subscriber.strip())

    def subscriber_exists(self, subscriber: str):
        for sub in self.subscribers:
            if sub == subscriber:
                return True
            
        return False

    def add_subscriber(self, subscriber: str):
        if self.subscriber_exists(subscriber):
            return

        self.subscribers.append(subscriber)
        self.save()

    def remove_subscriber(self, susbcriber: str):
        new_subscribers = []

        for sub in self.subscribers:
            if sub != susbcriber:
                new_subscribers.append(sub)

        self.subscribers = new_subscribers
        self.save()

    def save(self):
        with open(self.file_name, 'w+') as file:
            file.write('\n'.join(self.subscribers))
            file.write('\n')


class TelegramBot:

    def __init__(self, token: str, subscriber_manager: SubscriberManager):
        self.application = ApplicationBuilder().token(token).build()
        self.subscriber_manager = subscriber_manager

    def init(self):
        self._init_handlers()
        self._init_jobs()

    def _init_jobs(self):
        job_queue = self.application.job_queue

        for subscriber in self.subscriber_manager.subscribers:
            job_queue.run_repeating(self._level_alarm,
                                    interval=int(os.environ.get('LEVEL_POLLING_INTERVAL', 3600)),
                                    chat_id=int(subscriber),
                                    name=subscriber)

    def start(self):
        self.application.run_polling()

    async def _start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = 'Welcome to the <b>Water Sensor Bot</b>!\n\nThis bot was developed to notify you about the high level of water in a bucket on the balcony.\n\nTo subscribe for updates type /subscribe\n\n.For full list of commands type /help.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    def remove_alarm_job(self, name: str, context: ContextTypes.DEFAULT_TYPE):
        current_jobs = context.job_queue.get_jobs_by_name(name)
        
        if not current_jobs:
            return False
        
        for job in current_jobs:
            job.schedule_removal()

        self.subscriber_manager.remove_subscriber(name)

        return True
    
    def create_alarm_job(self, name: str, context: ContextTypes.DEFAULT_TYPE):
        context.job_queue.run_repeating(self._level_alarm,
                                        interval=int(os.environ.get('LEVEL_POLLING_INTERVAL', 3600)), 
                                        chat_id=int(name),
                                        name=name)
        self.subscriber_manager.add_subscriber(name)

    async def _subscribe_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        self.remove_alarm_job(str(chat_id), context)
        self.create_alarm_job(str(chat_id), context)
        
        msg = 'You have successfully subscribed for notifications! To unsubscribe type /unsubscribe'
        await update.effective_message.reply_text(text=msg)

    async def _unsubscribe_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self._remove_job_if_exists(str(chat_id), context)
        msg = 'You\'ve ubsubscribed from notifications. To subscribe type /subscribe.'
        await update.effective_message.reply_text(text=msg)

    def _get_water_level(self):
        file = open(os.environ.get('LEVEL_PATH'), 'r')
        level = file.read().strip()
        file.close()
        return level

    async def _level_alarm(self, context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        level = self._get_water_level()

        if float(level) > float(os.environ.get('LEVEL_LIMIT', 0)):
            return

        msg = '<b>ALARM!</b> Current water level: {level} cm.'.format(level=level.strip())
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
        # commands
        self.application.add_handler(CommandHandler('start', self._start_handler))
        self.application.add_handler(CommandHandler('subscribe', self._subscribe_handler))
        self.application.add_handler(CommandHandler('unsubscribe', self._unsubscribe_handler))
        self.application.add_handler(CommandHandler('help', self._help_handler))
        self.application.add_handler(CommandHandler('level', self._level_handler))

        # fallback handler
        self.application.add_handler(MessageHandler(filters.ALL, self._unknow_handler))

