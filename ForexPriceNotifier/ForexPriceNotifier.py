# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from Settings.forexConfig import CurrencyType, ForexType, PriceType
from ForexCrawler.ESunForexCrawler import ESunForexCrawler
from datetime import timedelta, datetime

import time

class ForexNotifyInfo:

    def __init__(self):
        self.__notified_interval = 10 # minutes
        self.__currency_dict = {}
        self.__last_notify_time = {}

    def __is_notify_valid(self, last_notify_time, cur_time = None):
        """Check if the notifies interval is over 10 minutes.
        :return
            Return True if the interval > 10 minutes
        """
        if last_notify_time is None:
            return True

        if cur_time is None:
            cur_time = datetime.now()

        diff = cur_time - last_notify_time
        if diff.seconds / 60 >= self.__notified_interval:
            return True

        return False

    def add_notify(self, currency, price):
        if type(price) is float or type(price) is int:
            self.__currency_dict[currency] = price

    def has_notify(self, currency):
        return self.__currency_dict.get(currency)

    def is_empty(self):
        return len(self.__currency_dict) == 0

    def remove_notify(self, currency):
        self.__currency_dict.pop(currency)

    def get_matched_notify(self, currency_now):
        """
        Check if given currency matches the set price.

        :param
            currency_now (dict): Current currency data from web.
        :return
            Return none empty string if matched set currency and price.
        """
        msg = ""
        num = 1
        for currency, price in self.__currency_dict.items():
            key = currency[:currency.rfind("-")]
            if key not in currency_now.keys():
                print("幣別無法由資料中取得: %s" % (key))
                continue

            if not self.__is_notify_valid(self.__last_notify_time.get(currency)):
                continue

            self.__last_notify_time[currency] = datetime.now()
            if ForexType.Buy.value in currency or ForexType.Sell.value in currency:
                if PriceType.Below.value in currency and price >= currency_now[key]:
                    msg += "\t%d.  %s : %s\n" % (num, currency, str(price))
                elif PriceType.Exceed.value in currency and price <= currency_now[key]:
                    msg += "\t%d.  %s : %s\n" % (num, currency, str(price))
            num += 1

        return msg

    def get_notify_info(self):
        info = ""
        num = 1
        for currency, price in self.__currency_dict.items():
            index = currency.find("-")
            index2 = currency.find("-", index + 1)
            info += "%d. %s %s %s %s\n" % (
            num, currency[index + 1: index2], currency[:index], currency[index2 + 1:], str(price))
            num += 1
        return info

class ForexSubscriber:
    @abstractmethod
    def update(self, user_id, message):
        pass

class ForexNotifier:

    def __init__(self, refresh_interval = 10000):
        self.currency_notify_dict = {}
        self.currency_wanted_list = []
        self.currency_refresh_interval = refresh_interval #ms
        self.stop_ = False
        self.subscribers_set_ = set()
        self.currency_filter = set()

    def addSubscriber(self, subscriber):
        self.subscribers_set_.add(subscriber)

    def removeSubscriber(self, subscriber):
        self.subscribers_set_.discard(subscriber)

    def is_type(self, object, t):
        if type(object) is not t:
            print("%s type is wrong" % (str(object)))
            return False
        return True

    def addNotify(self, user_id, currency_type, currency_price, forex_type, price_type):
        """
        Set notify condition when price reach the settings

        Args:
            user_id (str): Line user id to send notify.
            currency_type (CurrencyType): Currency type to set target price.
            currency_price (float): Target currency price.
            forex_type (ForexType): Set the price for buying or selling.
            price_type (PriceType): The type indicates notify when exceed or below target price.

        Returns:
            Return True if adding currency successfully.

        """
        if not self.is_type(currency_price, float) and not self.is_type(currency_price, int):
            return False
        if not self.is_type(currency_type, CurrencyType):
            return False
        if not self.is_type(forex_type, ForexType):
            return False
        if not self.is_type(price_type, PriceType):
            return False

        self.currency_filter.add(currency_type.value)
        key = self.compose_currency_key(currency_type, forex_type, price_type)

        forex_notify_info = self.currency_notify_dict.get(user_id)
        if forex_notify_info is None:
            forex_notify_info = ForexNotifyInfo()
        forex_notify_info.add_notify(key, currency_price)

        self.currency_notify_dict[user_id] = forex_notify_info

        return True

    def removeNotify(self, user_id, currency_type, forex_type, price_type):
        """
        Remove set notify currency.

        Args:
            currency_type (CurrencyType): Currency type to remove target price. eg. 美元(USD)
            forex_type (ForexType): The price for buying or selling.
            price_type (PriceType): The type indicates notify when exceed or below target price.

        """
        if not self.is_type(currency_type, CurrencyType):
            return False
        if not self.is_type(forex_type, ForexType):
            return False
        if not self.is_type(price_type, PriceType):
            return False
        if user_id not in self.currency_notify_dict.keys():
            return False

        key = self.compose_currency_key(currency_type, forex_type, price_type)
        if not self.currency_notify_dict[user_id].has_notify(key):
            print("尚未設定任何通知。")
            return False
        self.currency_notify_dict[user_id].remove_notify(key)
        print("通知已移除: %s" % (key))

        return True

    @staticmethod
    def compose_currency_key(currency_type, forex_type, price_type):
        return str(currency_type.value) + "-" + str(forex_type.value) + "-" + str(price_type.value)

    def notify_if_required(self, currency_now, date_time):
        message = ""
        notify_msg = ""
        for user_id, notify_info in self.currency_notify_dict.items():
            notify_msg = notify_info.get_matched_notify(currency_now)
            if len(notify_msg) > 0:
                message = "當前報價時間: %s\n" % (date_time)
                message += "到價通知:\n"
                message += notify_msg
                for subscriber in self.subscribers_set_:
                    subscriber.update(user_id, message)

        print(message)
        return message

    def start(self, crawler):
        """Loop for retrieving forex data from website and check if the set price is reached."""
        while len(self.currency_notify_dict) > 0:
            if self.stop_:
                self.stop_ = False
                print("中斷運作")
                break
            print("持續運作")
            if crawler.retrieveForexData():
                currency_now = crawler.getCurrency(self.currency_filter)
                effective_time = crawler.getEffectiveTime()
                self.notify_if_required(currency_now, effective_time)

            time.sleep(self.currency_refresh_interval / 1000)

    def stop(self):
        self.stop_ = True

    def get_notify_currency_info(self, user_id):
        """Display set notify currency"""
        info = ""
        if not self.currency_notify_dict.get(user_id) or self.currency_notify_dict[user_id].is_empty():
            info = "尚未設定任何通知"
        else:
            info = "目前設定通知:\n"
            info += self.currency_notify_dict[user_id].get_notify_info()

        return info

if __name__ == "__main__":
    notifier = ForexNotifier(10 * 1000)
    notifier.addNotify(0, CurrencyType.USD, 30.8, ForexType.Buy, PriceType.Exceed)
    notifier.addNotify(0, CurrencyType.JPY, 0.269, ForexType.Buy, PriceType.Exceed)
    print(notifier.get_notify_currency_info(0))
    #print(notifier.get_notify_currency_info(1))
    notifier.start(ESunForexCrawler())