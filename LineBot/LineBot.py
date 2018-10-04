from ForexPriceNotifier.ForexPriceNotifier import *
import Settings.config
import threading

from linebot import LineBotApi

from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

class ForexNotifierLineBot(ForexSubscriber):
    """Broadcast to line users when currency price reached setting target."""

    def __init__(self):
        self.__line_bot_api = LineBotApi(Settings.config.line_access_token)
        self.__notifier = ForexNotifier()
        self.__notifier.addSubscriber(self)
        self.__line_user_ids = set()
        self.__worker_thread = None

    def addNotifyCurrency(self, currency_type, currency_price, forex_type, price_type):
        self.__notifier.addWantedCurrency(currency_type)
        return self.__notifier.addNotify(currency_type, currency_price, forex_type, price_type)

    def update(self, msg):
        print(msg)
        for user_id in self.__line_user_ids:
            self.__line_bot_api.push_message(user_id, TextSendMessage(msg))

    def run(self):
        """Start a thread to get forex data and notify user when needed."""
        if self.__worker_thread is None:
            self.__worker_thread = threading.Thread(target=self.__notifier.start)
            self.__worker_thread.start()

    def stop(self):
        """Stop the worker thread and wait until it finished."""
        self.__notifier.stop()
        if self.__worker_thread is not None:
            self.__worker_thread.join()
            self.__worker_thread = None

    def addUserId(self, user_id):
        """Add line user id to push messages."""
        self.__line_user_ids.add(user_id)

    def removeUserId(self, user_id):
        """Remove line user id from push messages."""
        self.__line_user_ids.discard(user_id)

    def replyMessage(self, reply_token, msg):
        self.__line_bot_api.reply_message(reply_token, TextSendMessage(text=msg))