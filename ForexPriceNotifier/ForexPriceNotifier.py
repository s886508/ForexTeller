from ForexCrawler.ESunForexCrawler import ESunForexCrawler
from enum import Enum
import time

class ForexType(Enum):
    Buy = "Buy"
    Sell = "Sell"

class ForexNotifier:

    def __init__(self, wanted_list, refresh_interval = 10000):
        self.crawler_ = ESunForexCrawler()
        self.currency_notify_dict = {}
        self.currency_wanted_list = wanted_list
        self.currency_refresh_interval = refresh_interval #ms
        self.stop_ = False

    def setNotify(self, currency_type, currency_price, forex_type):
        """
        Set notify condition when price reach the settings

        Args:
            currency_type (str): Currency type to set target price. eg. 美元(USD)
            currency_price (float): Target currency price.
            forext_type (ForexType): Set the price for buying or selling.

        """
        if type(currency_price) is not float and type(currency_price) is not int:
            print("Parameter type is wrong. Please check.")
            return False

        if not currency_type:
            print("Currency string is empty.")
            return False

        key = currency_type + "-" + str(forex_type.value)
        self.currency_notify_dict[key] = currency_price

        return True

    def retrieveForexAndNotify(self):
        self.crawler_.retrieveForexData(self.crawler_.url_)
        cur_currency_price_dict = self.crawler_.getCurrency(self.currency_wanted_list)
        if len(self.currency_notify_dict) == 0:
            print("Cannot get currency data. The tool will be stopped.")
            return False

        for currency, price in self.currency_notify_dict.items():
            if currency not in cur_currency_price_dict.keys():
                print("The set currency: %s cannot be found from the site." % (currency))
                return False
            if "Buy" in currency and price >= self.currency_notify_dict[currency]:
                self.notify(currency, price)
            if "Sell" in currency and price <= self.currency_notify_dict[currency]:
                self.notify(currency, price)

        return True

    def notify(self, currency, price):
        message = "The following currency has reached set price:"
        message += "\t%s : %s" % (currency, str(price))
        print(message)
        return message

    def start(self):
        while len(self.currency_notify_dict) > 0:
            if self.stop_:
                self.stop_ = False
                break

            self.retrieveForexAndNotify()
            time.sleep(self.currency_refresh_interval / 1000)

    def stop(self):
        self.stop_ = True

if __name__ == "__main__":
    notifier = ForexNotifier(["美元(USD)", "日圓(JPY)"], 30 * 1000)
    notifier.setNotify("美元(USD)", 30.4, ForexType.Sell)
    notifier.setNotify("日圓(JPY)", 0.27, ForexType.Buy)
    notifier.start()