# -*- coding: utf-8 -*-
from forex.forex_notifier import ForexSubscriber

class ForexSubscriberMock(ForexSubscriber):

    def __init__(self):
        self.update_msg = ""

    def update(self, user_id, message):
        self.update_msg = message