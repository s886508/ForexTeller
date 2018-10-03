from ForexCrawler.ESunForexCrawler import ESunForexCrawler
from enum import Enum
import time

class ForexType(Enum):
    Buy = "Buy"
    Sell = "Sell"

class PriceType(Enum):
    Below = "Below"
    Exceed = "Exceed"

class ForexNotifier:

    def __init__(self, wanted_list, refresh_interval = 10000):
        self.crawler_ = ESunForexCrawler()
        self.currency_notify_dict = {}
        self.currency_wanted_list = wanted_list
        self.currency_refresh_interval = refresh_interval #ms
        self.stop_ = False

    def addNotify(self, currency_type, currency_price, forex_type, price_type):
        """
        Set notify condition when price reach the settings

        Args:
            currency_type (str): Currency type to set target price. eg. 美元(USD)
            currency_price (float): Target currency price.
            forex_type (ForexType): Set the price for buying or selling.
            price_type (PriceType): The type indicates notify when exceed or below target price.

        """
        if type(currency_price) is not float and type(currency_price) is not int:
            print("Parameter type is wrong. Please check.")
            return False

        if not currency_type:
            print("Currency string is empty.")
            return False

        key = self.composeCurrencyKey(currency_type, forex_type, price_type)
        self.currency_notify_dict[key] = currency_price

        return True

    def removeNotify(self, currency_type, forex_type, price_type):
        """
        Remove set notify currency.

        Args:
            currency_type (str): Currency type to remove target price. eg. 美元(USD)
            forex_type (ForexType): The price for buying or selling.
            price_type (PriceType): The type indicates notify when exceed or below target price.

        """
        if not currency_type:
            print("Currency string is empty.")
            return False

        key = self.composeCurrencyKey(currency_type, forex_type, price_type)
        if key not in self.currency_notify_dict.keys():
            print("You have not set the notify condition yet.")
            return False
        price = self.currency_notify_dict.pop(key)
        print("The notify has been removed: %s %f" % (key, price))

        return True

    def composeCurrencyKey(self, currency, forex_type, price_type):
        return currency + "-" + str(forex_type.value) + "-" + str(price_type.value)

    def matchCurrencyPrice(self, currency, price):
        """
        Check if given currency matches the set price.

        Args:
            currency (str): Currency to check if reach the set price.
            price (float): Price to check the set value.
        Returns:
            Return True if matched the set price for given currency.
        """
        if self.currency_notify_dict.get(currency) == None:
            print("The currency: %s does not call setNotify." % (currency))
            return False
        if type(price) is not float and type(price) is not int:
            print("Parameter type is wrong. Please check.")
            return False
        if "Buy" in currency:
            if "Below" in currency and price <= self.currency_notify_dict[currency]:
                return True
            elif "Exceed" in currency and price >= self.currency_notify_dict[currency]:
                return True
        if "Sell" in currency:
            if "Below" in currency and price <= self.currency_notify_dict[currency]:
                return True
            elif "Exceed" in currency and price >= self.currency_notify_dict[currency]:
                return True
        return False

    def notifyIfRequired(self, currency_dict, date_time):
        message = ""
        currency_msg = ""
        num = 1
        for currency, price in self.currency_notify_dict.items():
            tmp = currency.replace("-Exceed", "").replace("-Below", "")
            if tmp not in currency_dict.keys():
                print("The set currency: %s cannot be found from the site." % (currency))
                continue
            elif self.matchCurrencyPrice(currency, price):
                currency_msg += "\t%d.  %s : %s\n" % (num, currency, str(price))
                num += 1

        if len(currency_msg) > 0:
            message = "Current time: %s\n" % (date_time)
            message += "The following currency has reached set price:\n"
            message += currency_msg

        print(message)
        return message

    def start(self):
        """Loop for retrieving forex data from website and check if the set price is reached."""
        while len(self.currency_notify_dict) > 0:
            if self.stop_:
                self.stop_ = False
                break

            self.crawler_.retrieveForexData(self.crawler_.url_)
            self.notifyIfRequired(self.__retrieveWantedCurrency(), self.crawler_.getEffectiveTime())

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


    def __retrieveWantedCurrency(self):
        """Get forex data from website for wanted currency."""
        cur_currency_price_dict = self.crawler_.getCurrency(self.currency_wanted_list)
        if len(cur_currency_price_dict) == 0:
            print("Cannot get currency data. The tool will be stopped.")
            return {}

        return cur_currency_price_dict

if __name__ == "__main__":
    notifier = ForexNotifier(["美元(USD)", "日圓(JPY)"], 30 * 1000)
    notifier.addNotify("美元(USD)", 30.4, ForexType.Sell, PriceType.Exceed)
    notifier.addNotify("日圓(JPY)", 0.27, ForexType.Buy, PriceType.Below)
    notifier.showNotifyCurrency()
    notifier.start()