from ForexCrawler import ESunForexCrawler
from enum import Enum
import time

class ForexType(Enum):
    Buy = 0
    Sell = 1

class ForexNotifier:

    def __init__(self, wanted_list, refresh_interval):
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
        if forex_type == ForexType.Buy:
            key = currency_type + "-Buy"
        else:
            key = currency_type + "-Sell"
        self.currency_notify_dict[key] = currency_price

    def retrieveForexAndNotify(self):
        html_text = ESunForexCrawler.retrieveForexData()
        cur_currency_price_dict = ESunForexCrawler.getCurrency(html_text, self.currency_wanted_list)
        if len(self.currency_notify_dict) == 0:
            print("Cannot get currency data. The tool will be stopped.")
            return

        for currency, price in self.currency_notify_dict.items():
            if currency not in cur_currency_price_dict.keys():
                break
            if "Buy" in currency and price >= self.currency_notify_dict[currency]:
                self.notify(currency, price)
                break
            if "Sell" in currency and price <= self.currency_notify_dict[currency]:
                self.notify(currency, price)
                break

    def notify(self, currency, price):
        print("The following currency has reached set price:")
        print("\t" + currency + " : " + str(price))

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
    notifier.start()