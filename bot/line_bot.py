# -*- coding: utf-8 -*-
from forex.forex_notifier import *
from forex.esun_forex_crawler import ESunForexCrawler
from .settings import config

from linebot import LineBotApi
from linebot.models import (
    TextSendMessage,
)

class ForexNotifierLineBot(ForexSubscriber):
    """Broadcast to line users when currency price reached setting target."""

    def __init__(self):
        self.__line_bot_api = LineBotApi(config.line_access_token)
        self.__register_user_ids = set()

    def update(self, user_id, msg):
        self.pushMessage(user_id, msg)

    def addUserId(self, user_id):
        """Add line user id to push messages."""
        self.__register_user_ids.add(user_id)

    def removeUserId(self, user_id):
        """Remove line user id from push messages."""
        self.__register_user_ids.discard(user_id)

    def replyMessage(self, reply_token, msg):
        self.__line_bot_api.reply_message(reply_token, TextSendMessage(text=msg))

    def pushMessage(self, user_id, msg):
        self.__line_bot_api.push_message(user_id, TextSendMessage(text=msg))

    def get_notify_user_count(self):
        return len(self.__register_user_ids)