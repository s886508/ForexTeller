from abc import ABCMeta, abstractmethod
from Settings.forexConfig import CurrencyType, ForexType, PriceType
from ForexCrawler.ESunForexCrawler import ESunForexCrawler

import time

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
        key = self.composeCurrencyKey(currency_type, forex_type, price_type)
        if not self.currency_notify_dict.get(user_id):
            self.currency_notify_dict[user_id] = {}
        self.currency_notify_dict[user_id].update({key: currency_price})

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

        key = self.composeCurrencyKey(currency_type, forex_type, price_type)
        if key not in self.currency_notify_dict[user_id].keys():
            print("尚未設定任何通知。")
            return False
        price = self.currency_notify_dict[user_id].pop(key)
        print("通知已移除: %s %f" % (key, price))

        return True

    def composeCurrencyKey(self, currency_type, forex_type, price_type):
        return str(currency_type.value) + "-" + str(forex_type.value) + "-" + str(price_type.value)

    def matchCurrencyPrice(self, notify_dict, currency, price):
        """
        Check if given currency matches the set price.

        Args:
            currency (str): Currency to check if reach the set price.
            price (float): Price to check the set value.
        Returns:
            Return True if matched the set price for given currency.
        """
        if notify_dict.get(currency) == None:
            print("The currency: %s does not call setNotify." % (currency))
            return False
        if type(price) is not float and type(price) is not int:
            print("Parameter type is wrong. Please check.")
            return False
        if "Buy" in currency:
            if "Below" in currency and price <= notify_dict[currency]:
                return True
            elif "Exceed" in currency and price >= notify_dict[currency]:
                return True
        if "Sell" in currency:
            if "Below" in currency and price <= notify_dict[currency]:
                return True
            elif "Exceed" in currency and price >= notify_dict[currency]:
                return True
        return False

    def notifyIfRequired(self, currency_dict, date_time):
        message = ""
        currency_msg = ""
        num = 1
        for user_id, notify_dict in self.currency_notify_dict.items():
            for currency, price in notify_dict.items():
                tmp = currency.replace("-Exceed", "").replace("-Below", "")
                if tmp not in currency_dict.keys():
                    print("幣別無法由資料中取得: %s" % (currency))
                    continue
                elif self.matchCurrencyPrice(notify_dict, currency, price):
                    currency_msg += "\t%d.  %s : %s\n" % (num, currency, str(price))
                    num += 1

            if len(currency_msg) > 0:
                message = "當前報價時間: %s\n" % (date_time)
                message += "到價通知:\n"
                message += currency_msg
                for subscriber in self.subscribers_set_:
                    subscriber.update(user_id, message)

        #print(message)
        return message

    def start(self, crawler):
        """Loop for retrieving forex data from website and check if the set price is reached."""
        while len(self.currency_notify_dict) > 0:
            if self.stop_:
                self.stop_ = False
                break

            if crawler.retrieveForexData():
                currency_now = crawler.getCurrency(self.currency_filter)
                effective_time = crawler.getEffectiveTime()
                self.notifyIfRequired(currency_now, effective_time)

            time.sleep(self.currency_refresh_interval / 1000)

    def stop(self):
        self.stop_ = True

    def showNotifyCurrency(self):
        """Display set notify currency"""
        if len(self.currency_notify_dict) == 0:
            print("You have not set any currency for notifier.")

        print("Currency to notify now:")
        for currency, price in self.currency_notify_dict.items():
            print("\t%s : %s" % (currency, price))

if __name__ == "__main__":
    notifier = ForexNotifier(30 * 1000)
    notifier.addNotify(0, CurrencyType.USD, 30.4, ForexType.Sell, PriceType.Exceed)
    notifier.addNotify(0, CurrencyType.JPY, 0.27, ForexType.Buy, PriceType.Below)
    notifier.showNotifyCurrency()
    notifier.start(ESunForexCrawler())